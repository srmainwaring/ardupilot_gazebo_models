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

## Tuning physics

Adjusting the physics parameters is essential for a stable simulation. We obtained
good results with the `ode` `quick` solver with the following parameters.

### `<physics>`

```xml
<physics type='ode'>
    <max_step_size>0.001</max_step_size>
    <ode>
        <solver>
            <type>quick</type>
            <min_step_size>0.0001</min_step_size>
            <iter>50</iter>
            <sor>1.3</sor>
        </solver>
        <constraints>
            <cfm>1.0e-5</cfm>
            <erp>0.2</erp>
            <contact_max_correcting_vel>0.1</contact_max_correcting_vel>
            <contact_surface_layer>0.001</contact_surface_layer>
        </constraints>
    </ode>
</physics>
```

### `<link>`

A spherical collision is added to the end of the tibia. In Gazebo this
link is lumped in with the tibia so there is no need to provide a
visual or inertial (in fact supplying an inertial will offset the CoM
and distort the inertial for the tibia). The `<gazebo>` element for
the foot contains friction and contact parameters which are imported
into the correct locations when the SDF is generated.

The friction coefficients are needed to stop the foot sliding.
The contact parameters prevent the model from 'jittering' when using
the `quick` solver.

```xml
<xacro:macro name="gazebo_foot_link" params="reference">
    <gazebo reference="${reference}">
        <collision>
            <surface>
                <friction>
                    <ode>
                        <mu1>1.0</mu1>
                        <mu2>1.0</mu2>
                        <fdir1>1 0 0</fdir1>
                    </ode>
                    <torsional>
                        <coefficient>1.0</coefficient>
                        <surface_radius>${foot_radius}</surface_radius>
                        <use_patch_radius>false</use_patch_radius>
                    </torsional>
                </friction>
                <contact>
                    <ode>
                        <kp>1.0e+15</kp>
                        <kd>1.0e+13</kd>
                    </ode>
                </contact>
            </surface>
        </collision>
    </gazebo>
</xacro:macro>
```


