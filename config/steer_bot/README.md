# SteerBot with ArduPilot

This is a Gazebo model of a simple rover with Ackermann steering geometry integrated with ArduPilot.

## Running the simulation

The model requires a custom mixer for the servo outputs which is implemented using
a Lua script available in the `./config/steer_bot/scripts` directory. SITL will
need to be configured to use scripting: see the Ardupilot documentation [Lua Scripts](https://ardupilot.org/rover/docs/common-lua-scripts.html?highlight=lua#lua-scripts) for more detail.

### Start Gazebo

```bash
# start an empty world with containing the vehicle
$ gazebo --verbose 
```

### Start SITL

```bash
# start SITL using the JSON backend and save logs in the folder ./steer_bot
$ sim_vehicle.py --vehicle Rover --frame JSON --aircraft=steer_bot --console --map
```

### Servo Mixer

The servo mixer retrieves the yaw and throttle control outputs and calculates the
steering angles for the front wheels and speed commands for the rear wheels.

The rear wheels are both assigned the same speed commands (diff-locked) so the
rear wheels will need to skid slightly when turning.

The front wheels are not driven and only steer. The wheel angle is calculated
by scaling the input steering command (yaw) between zero and the maximum steering
angle (in this case 45 deg). This wheel angle is used to set the angle of the inside
front wheel and determine the turning radius for the vehicle. The turning radius is then
used to calculate the wheel angle of the outside front wheel.

### Parameters

Enable Lua scripting by setting `SCR_ENABLE = 1`, refresh parameters and restart. 

A full parameter set for the rover is saved in `./config/steer_bot/params/steer_bot.parm`.
The key parameters are:

**Scripting**

```bash
# Enable scripting and you may need to increase the memory available
SCR_ENABLE       1
SCR_HEAP_SIZE    65536
```

**Servos**

```bash
# The first 4 servos are controlled by the Lua script
SERVO1_FUNCTION  94
SERVO1_MAX       2000
SERVO1_MIN       1000
SERVO1_TRIM      1500
SERVO2_FUNCTION  95
SERVO2_MAX       2000
SERVO2_MIN       1000
SERVO2_TRIM      1500
SERVO3_FUNCTION  96
SERVO3_MAX       2000
SERVO3_MIN       1000
SERVO3_TRIM      1500
SERVO4_FUNCTION  97
SERVO4_MAX       2000
SERVO4_MIN       1000
SERVO4_TRIM      1500
```

**RC**

```bash
RC1_MAX          2000
RC1_MIN          1000
RC1_TRIM         1500
RC3_MAX          2000
RC3_MIN          1000
RC3_TRIM         1500
```
