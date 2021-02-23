# JetBoat with ArduPilot

This is a Gazebo model of a jet boat with twin reversible thrusters integrated with ArduPilot.

## Running the simulation

The model requires a custom mixer for the servo outputs which is implemented using
a Lua script available in the `./config/jet_boat/scripts` directory. SITL will
need to be configured to use scripting: see the Ardupilot documentation [Lua Scripts](https://ardupilot.org/rover/docs/common-lua-scripts.html?highlight=lua#lua-scripts) for more detail.

### Start Gazebo

```bash
# start an empty world with containing the vehicle
$ gazebo --verbose 
```

### Start SITL

```bash
# start SITL using the JSON backend and save logs in the folder ./jet_boat
$ sim_vehicle.py --vehicle Rover --frame JSON --aircraft=jet_boat --console --map
```

### Servo Mixer


### Parameters

Enable Lua scripting by setting `SCR_ENABLE = 1`, refresh parameters and restart. 

A full parameter set for the rover is saved in `./config/jet_boat/params/jet_boat.parm`.
The key parameters are:

**Scripting**

```bash
# Enable scripting and you may need to increase the memory available
SCR_ENABLE       1
SCR_HEAP_SIZE    65536
```

**Servos**

- SERVO1 - left thruster
- SERVO2 - right thruster
- SERVO3 - left thrust reverser
- SERVO4 - right thrust reverser
- SERVO5 - left rudder
- SERVO6 - right rudder
- SERVO7 - dummy to indicate skid-steering (left throttle)
- SERVO8 - dummy to indicate skid-steering (right thottle)


```bash
# The first 4 servos are controlled by the Lua script
SERVO1_FUNCTION  94
SERVO1_MAX       2000
SERVO1_MIN       1000
SERVO1_TRIM      1000
SERVO2_FUNCTION  95
SERVO2_MAX       2000
SERVO2_MIN       1000
SERVO2_TRIM      1000
SERVO3_FUNCTION  96
SERVO3_MAX       2000
SERVO3_MIN       1000
SERVO3_TRIM      1000
SERVO4_FUNCTION  97
SERVO4_MAX       2000
SERVO4_MIN       1000
SERVO4_TRIM      1000
SERVO5_FUNCTION  98
SERVO5_MAX       2000
SERVO5_MIN       1000
SERVO5_TRIM      1500
SERVO6_FUNCTION  99
SERVO6_MAX       2000
SERVO6_MIN       1000
SERVO6_TRIM      1500
SERVO7_FUNCTION  73
SERVO7_MAX       2000
SERVO7_MIN       1000
SERVO7_TRIM      1500
SERVO8_FUNCTION  74
SERVO8_MAX       2000
SERVO8_MIN       1000
SERVO8_TRIM      1500
```

**RC**

```bash
RC1_MAX          2000
RC1_MIN          1000
RC1_REVERSED     0
RC1_TRIM         1500
RC3_MAX          2000
RC3_MIN          1000
RC3_REVERSED     0
RC3_TRIM         1500
```
