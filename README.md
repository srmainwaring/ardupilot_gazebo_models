# ArduPilot Gazebo Models

Gazebo models that can be controlled with ArduPilot using the ArduPilot Gazebo plugin
([khancyr/ardupilot_gazebo](https://github.com/khancyr/ardupilot_gazebo)).

## Models

### [Sawppy](config/sawppy/README.md)

This is a Gazebo model of [Roger Chen's Sawppy Rover](https://github.com/Roger-random/Sawppy_Rover)
integrated with ArduPilot.

The controller for the model uses the ArduPilot Lua scripting framework to support the custom frame
and control the 6 wheel motors and 4 steering servos.

### [Quadruped](config/quadruped/README.md)

This is a Gazebo model of a Quadruped robot developed by Ashvath in this project: [GSoC 2020: Walking Robot Support For Ardupilot](https://discuss.ardupilot.org/t/gsoc-2020-walking-robot-support-for-ardupilot/57080).

The servo mixer for this model uses the ArduPilot Lua scripting framework.

### [SteerBot](config/steer_bot/README.md)

This is a simple Gazebo model of a rover with car steering and rear wheel drive.

The servo mixer for this model uses the ArduPilot Lua scripting framewortk.

### [JetBoat](config/jet_boat/README.md)

This is a simple Gazebo model of a jet boat with twin reversible thrusters.

The servo mixer for this model uses the ArduPilot Lua scripting framework.

### [FanCar](config/fan_car/README.md)

This is a Gazebo model of a board with castor wheels powered by a steerable rotor.

This toy model is an exerise in tuning a vehicle with almost no yaw control inspired
by this [ArduPilot Discord post](https://discord.com/channels/674039678562861068/674039678982422579/821309513805332500) by Peter Barker.

## License

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
[GNU General Public License](LICENSE) for more details.

