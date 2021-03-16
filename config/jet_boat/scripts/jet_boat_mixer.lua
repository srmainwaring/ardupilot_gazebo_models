--[[
    Copyright (c) 2021, Rhys Mainwaring

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
--]]

--[[
    Servo mixer for a twin-jet boat

    Vehicle control outputs are defined in AP_Vehicle::ControlOutput.

        CONTROL_OUTPUT_THROTTLE = 3
        CONTROL_OUTPUT_YAW = 4

    The output directed to servos using the enum defined in SRV_Channel::Aux_servo_function_t.
    For scripting the following parameters should be set:

        SERVO1_FUNCTION = 94
        SERVO2_FUNCTION = 95
        SERVO3_FUNCTION = 96
        SERVO4_FUNCTION = 97
        SERVO5_FUNCTION = 98
        SERVO6_FUNCTION = 99

        SERVO7_FUNCTION = 73 (in-place steer marker)
        SERVO8_FUNCTION = 74 (in-palce steer marker)
--]]

-- control outputs
local CONTROL_OUTPUT_THROTTLE = 3
local CONTROL_OUTPUT_YAW = 4

-- servo outputs
local SERVO1_FUNCTION = 94      -- left thruster
local SERVO2_FUNCTION = 95      -- right thruster
local SERVO3_FUNCTION = 96      -- left thrust reverser
local SERVO4_FUNCTION = 97      -- right thrust reverser
local SERVO5_FUNCTION = 98      -- left rudder
local SERVO6_FUNCTION = 99      -- right rudder

-- update at 50Hz
local UPDATE_PERIOD = 20

-- joint geometry for rover (FRD) relative to the lateral through the thrusters, units are [m]
local JOINT_COORDS = {}
JOINT_COORDS[1] = { 0.0, -0.3}      -- left thruster
JOINT_COORDS[2] = { 0.0,  0.3}      -- right thruster
JOINT_COORDS[3] = {-0.7, -0.3}      -- left rudder
JOINT_COORDS[4] = {-0.7,  0.3}      -- right rudder

local THRUSTER_SEP_W = 0.6          -- rudder lateral separation
local RUDDER_ANGLE_MAX_DEG = 45.0   -- rudder angle limit (one side)

--[[
    Constrain a value to a range

    Parameters
    ==========
    value : float
        The value to constrain
    min_value : float
        The lower limit of the range
    max_value : float
        The upper limit of the range

    Returns
    =======
    float
        A value constrained to the range
--]]
local function constrain(value, min_value, max_value)
    return math.max(math.min(value, max_value), min_value)
end

--[[
    Scale each element of a 2d array

    Parameters
    ==========
    vector : array
        The input array
    scale : float
        A scalar value

    Returns
    =======
    array
        The scaled array
--]]
local function scale_vector2d(vector, scale)
    local vector_out = {}
    for i=1, #vector do
        vector_out[i] = {vector[i][1] * scale, vector[i][2] * scale}
    end
    return vector_out
end

--[[
    Calculate the Euclidean distance between two points

    Parameters
    ==========
    a : array
        The first point
    b : array
        The second point

    Returns
    =======
    float
        The distance (L2 norm) between the two points
--]]
local function distance_vector2d(a, b)
    local dx = b[1] - a[1]
    local dy = b[2] - a[2]
    local r = math.sqrt(dx * dx + dy * dy)
    return r
end

--[[
    Apply skid-steering saturation limits to the scaled steering and throttle

    Adapted from ardupilot/Rover/AP_MotorsUGV::output_skid_steering

    Parameters
    ==========
    steering : float
        The steering control output in [-1, 1]
    throttle : float
        The throttle control output in [-1, 1]

    Returns
    =======
    steering, throttle : float, float
        The saturation limited scaled control outputs

--]]
local function apply_skid_steer_saturation_limits(steering, throttle)
    local steering_scaled = steering
    local throttle_scaled = throttle

    -- check for saturation and scale back steering and throttle
    local saturation_value = math.abs(steering_scaled) + math.abs(throttle_scaled)
    if saturation_value > 1.0 then
        local fair_scaler = 1.0 / saturation_value
        steering_scaled = steering_scaled * fair_scaler
        throttle_scaled = throttle_scaled * fair_scaler
    end

    return steering_scaled, throttle_scaled
end

--[[
    Calculate the motor outputs for skid steering from saturation limited control outputs

    Adapted from ardupilot/Rover/AP_MotorsUGV::output_skid_steering

    Parameters
    ==========
    steering : float
        The saturation limited steering control output in [-1, 1]
    throttle : float
        The saturation limited throttle control output in [-1, 1]

    Returns
    =======
    motor_left, motor_right : float, float
        The scaled left and right motor outputs in [-1, 1]
--]]
local function output_skid_steering(steering, throttle)
    local motor_left = throttle + steering
    local motor_right = throttle - steering
    return motor_left, motor_right
end

--[[
    Calculate the turning radius and rate about the instantaneous centre of curvature

    This calculation is in normalised coordinates. The origin of the body frame {B}
    is assumed to lie at the mid-point between the two wheels and the distance from
    the origin of {B} to each wheel is 1.

    IMPORTANT NOTE: this function assumes the steering and throttle are POSITIVE

    Parameters
    ==========
    steering : float
        The saturation limited steering control output in [0, 1]
    throttle : float
        The saturation limited throttle control output in [0, 1]

    Returns
    =======
    radius, rate : float, float
        The distance from the origin of the body frame {B} to the
         instantaneous centre of curvature frame P and the rate of turn
        of {B} about P.
--]]
local function turning_radius_and_rate(steering, throttle)
    -- left and right wheel velocities
    local v_l = throttle + steering
    local v_r = throttle - steering

    -- turning radius is infinite if steering is zero
    local r_p = math.huge
    local omega_p = 0
    if v_l ~= v_r then
        r_p = (v_l + v_r) / (v_l - v_r)
        omega_p = v_l / (r_p + 1)
    end

    return r_p, omega_p
end

--[[
    Rescale the wheel coordinates by the half the mid wheel separation

    The saturation limits for steering and throttle control are calculated
    in scaled coordinates assuming a wheel separation of 2.

    Parameters
    ==========
    wheel_coords : array
        The array of wheel coordinates (x, y)
    mid_wheel_sep : float
        The lateral distance between the left and right mid wheels

    Returns
    =======
    array
        The scaled (normalised) wheel coordinates

--]]
local function normalise_wheel_coordinates(wheel_coords, mid_wheel_sep)
    return scale_vector2d(wheel_coords, 2.0 / mid_wheel_sep)
end

--[[
    Calculate a wheel's distance from the instantaneous centre of curvature

    Parameters
    ==========
    icc : array
        The coordinates (x, y) of the instantaneous centre of curvature
    wheel_coords : array
        The (x, y) normalised wheel coordinates

    Returns
    =======
    float
        The distance

--]]
local function wheel_turning_radius(icc, wheel_coord)
    return distance_vector2d(icc,  wheel_coord)
end

--[[
    Rescale an array or turning radii so the maximum no greater than 1

    This function returns a normalised array of turning radii for the
    wheels. It ensures that the servo outputs are constainined to [0, 1].
    The radii are assumed positive.

    Parameters
    ==========
    r : array
        An array of turning radii (r[i] >= 0)

    Returns
    =======
    array
        The rescaled turning radii (array).
--]]
local function rescale_turning_radii(r)

    -- determine maximum
    local r_max = 0.0
    for i = 1, #r do
        if r[i] == math.huge then
            r_max = math.huge
            break
        else
            r_max = math.max(r_max, r[i])
        end
    end

    -- rescale
    local r_s = {}
    for i = 1, #r do
        if r_max == math.huge then
            r_s[i] = 1.0
        else
            r_s[i] = r[i] / r_max
        end
    end

    return r_s
end

--[[
    Calculate the wheel angle for a turn about a given ICC

    This function calculates the unconstrained steering angle for
    a wheel given and instantaneous centre of curvature (ICC). The
    output steering angle is in [-pi, pi]

    Parameters
    ==========
    icc : array
        An array (x, y) containing x and y coordinates of the ICC
    wheel_coord : array
        An array (x, y) containing x and y coordinates of a wheels axis

    Returns
    =======
    float
        The steering angle in radians. The angle is in [-pi, pi]
--]]
local function wheel_angle(icc, wheel_coord)
    local dx = icc[1] - wheel_coord[1]
    local dy = icc[2] - wheel_coord[2]
    local theta = math.atan(dx, dy)
    return theta
end

--[[
    Calculate the servo outputs for a rover from steering and throttle control

    This function calculates the output for each thruster and the
    rudder angles. The servo outputs are normalised to [-1, 1].

    The rudder angles are constrained [-RUDDER_ANGLE_MAX_DEG, RUDDER_ANGLE_MAX_DEG].

    Parameters
    ==========
    steering : float
        The normalised steering rate in [-1, 1]
    throttle : float
        The normalised throttle in [-1, 1]

    Returns
    =======
    thrusters, thrust_reversers, rudders : array, array, array
        Return the normalised servo outputs for 2 thrusters, 2 thrust reversers and two rudders
--]]
local function servo_outputs(steering, throttle)
    -- reverse steering when throttle reversed
    if throttle < 0  then
        steering = -steering
    end

    -- capture the sign of steering and throttle as main calc assumes steering, throttle > 0
    local steering_sign = 1
    if steering < 0 then
        steering_sign = -1
        steering = -steering
    end
    local throttle_sign = 1
    if throttle < 0 then
        throttle_sign = -1
        throttle = -throttle
    end

    -- saturation limited control outputs
    local steering_scaled, throttle_scaled = apply_skid_steer_saturation_limits(steering, throttle)

    -- skid steering motor outputs in normalised corrdinates
    local motor_left, motor_right = output_skid_steering(steering_scaled, throttle_scaled)
    local motor_out = math.max(math.abs(motor_left), math.abs(motor_right)) * throttle_sign

    -- instantaneous centre of curvature
    local r_p, omega_p = turning_radius_and_rate(steering, throttle)
    local icc = {0.0, r_p}

    -- normalised joint coordinates
    local wheel_coords = normalise_wheel_coordinates(JOINT_COORDS, THRUSTER_SEP_W)

    -- normalised turning radius for each wheel
    local r = {0.0, 0.0, 0.0, 0.0}
    for i = 1, #r do
        r[i] = wheel_turning_radius(icc, wheel_coords[i])
     end
     r = rescale_turning_radii(r)
 
    -- wheel speed and steering angles
    local wheels = {0.0, 0.0, 0.0, 0.0}
    local steers = {0.0, 0.0, 0.0, 0.0}
    for i = 1, #r do
        wheels[i] = motor_out * r[i]
        steers[i] = wheel_angle(icc, wheel_coords[i])

        -- apply steering constraints (rotate by 180 and reverse direction)
        if steers[i] > math.pi / 2.0 then
            wheels[i] = -wheels[i]
            steers[i] = steers[i] - math.pi
        end
        if steers[i] < -math.pi / 2.0 then
            wheels[i] = -wheels[i]
            steers[i] = steers[i] + math.pi
        end

        -- rescale steer outputs to [0, 1]
        steers[i] = steers[i] / math.pi

        -- enforce constraints
        wheels[i] = constrain(wheels[i], -1.0, 1.0)
        steers[i] = constrain(steers[i], -1.0, 1.0)
    end

    -- flip wheel speeds and steering angles and signs if steering < 0
    if steering_sign < 0 then
        for i = 1, #steers/2 do
            local tmp = wheels[2 * i - 1]
            wheels[2 * i - 1] = wheels[2 * i]
            wheels[2 * i] = tmp

            tmp = steers[2 * i - 1]
            steers[2 * i - 1] = -steers[2 * i]
            steers[2 * i] = -tmp
        end
    end

    local thrusters = {wheels[1], wheels[2]}
    local thrust_reversers = {0.0, 0.0}

    for i = 1, #thrusters do
        if thrusters[i] < 0 then
            thrusters[i] = - thrusters[i]
            thrust_reversers[i] = 1.0
        end
    end

    local rudders = {steers[3], steers[4]}

    -- debug output
    ---[[
    gcs:send_text(6,
        string.format("STR:%.2f THR:%.2f LT:%.2f RT:%.2f LRT:%.2f RRT:%.2f LR:%.2f RR:%.2f",
        steering, throttle,
        thrusters[1], thrusters[2],
        thrust_reversers[1], thrust_reversers[2],
        rudders[1], rudders[2]))
    --]]

    return thrusters, thrust_reversers, rudders
end

--[[
    Main update loop

    Poll the control outputs every UPDATE_PERIOD milli seconds,
    compute the servo outputs for wheels and steeing and send
    them to the servo channels.
--]]
local function update()
    -- retrieve high level steering and throttle control outputs
    local steering = vehicle:get_control_output(CONTROL_OUTPUT_YAW)
    local throttle = vehicle:get_control_output(CONTROL_OUTPUT_THROTTLE)

    -- compute servo outputs : {left = 1, right = 2}
    local thrusters = {0.0, 0.0}
    local thrust_reversers = {0.0, 0.0}
    local rudders = {0.0, 0.0}

    thrusters, thrust_reversers, rudders = servo_outputs(steering, throttle)

    -- thruster and thrust reverser servos only set when armed
    if not arming:is_armed() then
        -- if not armed move throttle to mid
        SRV_Channels:set_output_norm(SERVO1_FUNCTION, 0)
        SRV_Channels:set_output_norm(SERVO2_FUNCTION, 0)
        SRV_Channels:set_output_norm(SERVO3_FUNCTION, 0)
        SRV_Channels:set_output_norm(SERVO4_FUNCTION, 0)
    else
        SRV_Channels:set_output_norm(SERVO1_FUNCTION, thrusters[1])
        SRV_Channels:set_output_norm(SERVO2_FUNCTION, thrusters[2])
        SRV_Channels:set_output_norm(SERVO3_FUNCTION, thrust_reversers[1])
        SRV_Channels:set_output_norm(SERVO4_FUNCTION, thrust_reversers[2])
    end

    -- always allow rudders
    SRV_Channels:set_output_norm(SERVO5_FUNCTION, rudders[1])
    SRV_Channels:set_output_norm(SERVO6_FUNCTION, rudders[2])

    return update, UPDATE_PERIOD
end

gcs:send_text(6, "twin_jet_boat_mixer.lua is running")
return update(), 3000

