# Dolly with ArduPilot

This is a Gazebo model of a rotor powered dolly (a board on castor wheels) integrated with ArduPilot.
There are two variants, one has standard castor wheels with two axes (steering and wheel rotation),
the other uses ball castors which have three orthogonal axis of rotation.

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
# start SITL using the JSON backend and save logs in the folder ./jet_boat
$ sim_vehicle.py --vehicle Rover --frame JSON --aircraft=dolly --console --map
```

### Parameters

The throttle and motor output are configured for forward thrust only.

**Servos**

```bash
SERVO1_FUNCTION  26 (Ground Steering)
SERVO1_MAX       2000
SERVO1_MIN       1000
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
