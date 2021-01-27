# Quadruped with ArduPilot

This is a Gazebo model of a Quadruped robot integrated with ArduPilot.
The controller for this model is the result of Ashvath's project
[GSoC 2020: Walking Robot Support For Ardupilot](https://discuss.ardupilot.org/t/gsoc-2020-walking-robot-support-for-ardupilot/57080).

## Running the simulation

This model requires a custom controller which is implemented in the ArduPilot Lua script
[`quadruped.lua`](https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_Scripting/examples/quadruped.lua). There is a copy of this script in `ardupilot_gaszebo_models/config/quadruped/scripts`
for convenience.

Set up the rover and SITL following the ArduPilot wiki instructions for [Walking Robots](https://ardupilot.org/rover/docs/walking-robots.html).


### Start Gazebo

```bash
# start an empty world with containing the Quadruped
$ gazebo worlds/quadruped.world --verbose 
```

### Start SITL

```bash
# start SITL using the gsazebo-rover frame and save logs in the folder ./quadruped
$ sim_vehicle.py --vehicle Rover --frame JSON --aircraft=quadruped --console --map
```
