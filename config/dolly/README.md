# Dolly with ArduPilot

This is a Gazebo model of a rotor powered dolly (a board on castor wheels)
integrated with ArduPilot.
There are two variants, one has standard castor wheels with two axes
(steering and wheel rotation), the other uses ball castors which have
three orthogonal axes of rotation.

This is a toy model which can be used to investigate rover control tuning. It requires
careful tuning of the joint PID controllers used in `ardupilot_gazebo` in order to reduce
vibrations.

## Running the simulation

The model is controlled using standard rover servo outputs for ground steering and throttle. 

### Start Gazebo

```bash
# start an empty world with containing the vehicle
$ gazebo --verbose 
```

### Start SITL

```bash
# start SITL using the JSON backend and save logs in the folder ./dolly
$ sim_vehicle.py --vehicle Rover --frame JSON --aircraft=dolly --console --map
```

### Servo and RC parameters

**Servo**

The rotor steering joint in the model is configured with rotation limits
[-180, 180] deg. To help prevent the model spinning the servo parameters
are set to restrict the range of movement to ensure there is always a backwards
component to the thrust.

The motor is not permitted to reverse and the normalised servo output is in [0, 1]. 

```bash
SERVO1_FUNCTION  26 (Ground Steering)
SERVO1_MAX       1850
SERVO1_MIN       1150
SERVO1_REVERSED  0
SERVO1_TRIM      1500
SERVO3_FUNCTION  70 (Throttle)
SERVO3_MAX       2000
SERVO3_MIN       1000
SERVO3_REVERSED  0
SERVO3_TRIM      1000
```

**RC**

```bash
RC1_MAX          2000
RC1_MIN          1000
RC1_TRIM         1500
RC3_MAX          2000
RC3_MIN          1000
RC3_REVERSED     0
RC3_TRIM         1000
```

### Gazebo PID Tuning

The simulation joint controllers must be tuned to minimise vibrations which
would otherwise interfere with the autopilot EKF.

#### Steering (position controlled joint)

```console
p_gain:    10.0
i_gain:     0.1
d_gain:     0.02
i_max:      1.0
i_min:      0.0
cmd_max:  100.0
cmd_min: -100.0
```

#### Rotor (velocity contolled joint)

```console
p_gain:     0.005
i_gain:     0.0
d_gain:     1.0e-5
i_max:      0.1
i_min:      0.0
cmd_max:    5.0
cmd_min:   -5.0
```

### Throttle and steering tuning

```console
ARMING_RUDDER   0.0
CRUISE_SPEED    2.5
CRUISE_THROTTLE 40.0
ATC_ACCEL_MAX   0.3
ATC_BRAKE       0.0
ATC_SPEED_D     0.001
ATC_SPEED_FF    0
ATC_SPEED_I     0.005
ATC_SPEED_P     0.2
```

```bash
# steering requires an aggressive P gain  
ACRO_TURN_RATE  30.0
ATC_STR_RAT_D   0.01
ATC_STR_RAT_FF  0.75
ATC_STR_RAT_I   0.10
ATC_STR_RAT_P   4.00
```

```bash
# vector thrust and steering speed scaling
MOT_SPD_SCA_BASE 2.0
MOT_VEC_THR_BASE 30.0
```

### L1 Navigation tuning

This rover is configured as a boat which sets the AHRS fly_forward
to false.  This prevents the EKF from using the rovers's movement to
estimate heading which is important as the vehicle has very poor yaw control
and can easily drift sideways.

```bash
# set frame to boat
FRAME_CLASS     2.0

# L1 controller settings: see notes for details
NAVL1_DAMPING   2.37
NAVL1_PERIOD    21.0

# relax WP conditions
WP_OVERSHOOT    3.0
WP_RADIUS       3.0
WP_SPEED        1.0
WP_SPEED_MIN    0.0
```

The L1 navigation settings are very different from the values recommended on the wiki.
The vehicle has very poor yaw control and so the heading and course may be very
different even in the absence of environmental effects such as wind.
We tune the navigation controller by considering the L1 distance and maximum lateral
acceleration values rather than the damping and period parameters (which are then derived).

See the wiki entry [Rover: L1 navigation overview](https://ardupilot.org/dev/docs/rover-L1.html)
for a description of the parameters.

The oscillations about the direct course between waypoints can be reduced by increasing the
L1 distance (proportional to the square of the `NAVL1_PERIOD`). However the choice of period
and damping are tighly coupled as the lateral acceleration  must be achieved via the rotor thrust
having a lateral component rather than by the vehicles form or slip resistance. As a result we
fix a target speed and choose a maximum value for the lateral acceleration. The equations
for the L1 distance and lateral acceleration are rearranged to solve for the period
and damping:

```bash
period = (20/3) * sqrt(L1_dist / lat_accel_max)

damping = (10/3) * L1_dist / (period * speed)
```

The given NAVL1 controller parameters correspond to:

```bash
L1_dist         15
lat_accel_max   1.5
```
