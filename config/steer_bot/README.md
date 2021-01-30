# SteerBot with ArduPilot

This is a Gazebo model of a simple rover with Ackermann steering geometry integrated with ArduPilot. The model can be controlled with SITL using the standard rover configuration.

## Running the simulation

Set up the rover and SITL following the ArduPilot wiki instructions.

### Start Gazebo

```bash
# start an empty world with containing the Quadruped
$ gazebo --verbose 
```

### Start SITL

```bash
# start SITL using the JSON backend and save logs in the folder ./steer_bot
$ sim_vehicle.py --vehicle Rover --frame JSON --aircraft=steer_bot --console --map
```
