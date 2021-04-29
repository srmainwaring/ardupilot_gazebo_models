# Fan Car

This is a Gazebo model of a fan car, a rotor powered board on castor wheels,
integrated with ArduPilot.
There are two variants, one has standard castor wheels with two axes
(steering and wheel rotation), the other uses ball castors which have
three orthogonal axes of rotation.

This is a toy model which can be used to investigate rover control tuning. It requires
careful tuning of the joint PID controllers used in `ardupilot_gazebo` in order to reduce
vibrations.

## Quick start

The model is controlled using standard rover servo outputs for ground steering and throttle. 

### Start Gazebo

```bash
# start an empty world with containing the vehicle
$ gazebo --verbose 
```

### Start SITL

```bash
# start SITL using the JSON backend and save logs in the folder ./fan_car
$ sim_vehicle.py --vehicle Rover --frame JSON --aircraft=fan_car --console --map
```

## Simulation settings

The simulation joint controllers must be tuned to ensure the motor
responds rapidly to throttle commands while minimising vibrations which
would otherwise interfere with the autopilot EKF. The following settings
are used by the `ardupilot_gazebo` plugin:

### Steering (position controlled joint)

```xml
<control channel="0">
    <jointName>fan_car_ardupilot::fan_car::back_steer_rotor_joint</jointName>
    <useForce>1</useForce>
    <multiplier>3.141592653</multiplier>
    <offset>-0.5</offset>
    <servo_min>1000</servo_min>
    <servo_max>2000</servo_max>
    <type>POSITION</type>
    <p_gain>10</p_gain>
    <i_gain>0.1</i_gain>
    <d_gain>0.02</d_gain>
    <i_max>1</i_max>
    <i_min>-1</i_min>
    <cmd_max>100.0</cmd_max>
    <cmd_min>-100.0</cmd_min>
</control>
```

### Motor (velocity contolled joint)

```xml
<control channel="2">
    <jointName>fan_car_ardupilot::fan_car::back_motor_joint</jointName>
    <useForce>1</useForce>
    <multiplier>-800</multiplier>
    <offset>0</offset>
    <servo_min>1000</servo_min>
    <servo_max>2000</servo_max>
    <type>VELOCITY</type>
    <p_gain>0.007</p_gain>
    <i_gain>0.005</i_gain>
    <d_gain>0.0</d_gain>
    <i_max>0.1</i_max>
    <i_min>-0.1</i_min>
    <cmd_max>10.0</cmd_max>
    <cmd_min>-10.0</cmd_min>
</control>
```

### World physics settings 

A stable simulation can be obtained using the ODE `quick` integrator
with a slight modification to the default settings. The main
simulation defect to overcome is the wheel contact jitter, increasing
the contact surface layer parameter helps reduce this.  

```xml
<physics type='ode'>
    <max_step_size>0.001</max_step_size>
    <ode>
        <solver>
            <type>quick</type>
            <min_step_size>0.0001</min_step_size>
            <iters>50</iters> 
            <sor>1.3</sor>
        </solver>
        <constraints>
            <cfm>0.001</cfm>
            <erp>0.3</erp>
            <contact_max_correcting_vel>10.0</contact_max_correcting_vel>
            <contact_surface_layer>0.005</contact_surface_layer>
        </constraints>
    </ode>
</physics>
```

## Vehicle settings

The rover is configured as a vectored-thrust boat. Using the boat frame
prevents the EKF from using the rover's movement to estimate heading which
is important as the vehicle can drift sideways.

### Firmware

Install Rover 4.1 or greater.

### Vehicle and frame

```bash
FRAME_TYPE = 2 (Boat)
```

### RC

```bash
RC1_MAX          2000
RC1_MIN          1000
RC1_TRIM         1500

RC3_MAX          2000
RC3_MIN          1000
RC3_TRIM         1000 (No reverse)
```

### Servo

The rotor steering joint in the model is configured with rotation limits
[-180, 180] deg. To help prevent the model spinning the servo parameters
are set to restrict the range of movement to [-45, 45] deg which ensures
there is always a backwards component to the thrust.

The motor is not permitted to reverse and the normalised servo output is in [0, 1]. 

(**Note** this is different from the real rover which has joint limits
of [-45, 45] deg. The model should be updated to reflect this).

```bash
SERVO1_FUNCTION  26 (Ground Steering)
SERVO1_MAX       1750 (limit rotation to 45)
SERVO1_MIN       1250 (limit rotation to 45)
SERVO1_REVERSED  0
SERVO1_TRIM      1500

SERVO3_FUNCTION  70 (Throttle)
SERVO3_MAX       2000
SERVO3_MIN       1000
SERVO3_REVERSED  0
SERVO3_TRIM      1000
```

### Motors (vectored-thrust)

The vectored-thrust parameter must be set to the same deflection
range as the motor bracket [-45, 45] deg.

```bash
MOT_SPD_SCA_BASE  0
MOT_VEC_ANGLEMAX 45
MOT_SLEWRATE     70
```

### Throttle

```bash
ARMING_RUDDER   0
CRUISE_SPEED    2.0
CRUISE_THROTTLE 50.0
ATC_ACCEL_MAX   1.0
ATC_BRAKE       0
ATC_SPEED_P     0.4
ATC_SPEED_I     0.1
ATC_SPEED_D     0
ATC_SPEED_FF    0
```

### Steering

```bash
ACRO_TURN_RATE  90
ATC_STR_RAT_MAX 90
ATC_STR_RAT_P   0.3
ATC_STR_RAT_I   0.02
ATC_STR_RAT_D   0.01
ATC_STR_RAT_FF  0.1
```

### Navigation L1

```bash
NAVL1_DAMPING   0.75
NAVL1_PERIOD    15

WP_SPEED        1.5
```

## Appendix A: model calibration - thrust stand simulation

The purpose of the thrust stand simulation is to determine the damping and friction coefficients for the fan car motor joint and then select suitable PID controller gains in the ArduPilotGazebo plugin.

#### `sim_ardupilot_thrust_stand.py`

A Python script using `pcg_gazebo` to create the SDF model for the thrust stand and spawn it into Gazebo.

#### `publish_pids.py`

A Python script that uses `pygazebo` to publish PID messages on the Gazebo transport layer. A modified version of the ArduPilotGazebo plugin subscribes to these and updates the controller settings when they are received (see: [srmainwaring/ardupilot_gazebo: branch feature/sitl_json_dynamic_pid](https://github.com/srmainwaring/ardupilot_gazebo/tree/feature/sitl_json_dynamic_pid))


Run Gazebo with the ROS `gazebo_ros_pkgs` plugins enabled in verbose mode:

```bash
$ rosrun gazebo_ros gazebo --verbose
```


Run SITL-JSON:

```
$ sim_vehicle.py -v Rover -f JSON --aircraft=thrust_stand --console --map
```

