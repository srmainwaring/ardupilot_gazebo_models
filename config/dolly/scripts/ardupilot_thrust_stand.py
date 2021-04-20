#!/usr/bin/env python3

'''
ArduPilot: Thrust Stand

Script version of the Jupyter notebook `ardupilot_thrust_stand.ipynb`
'''

import math
import signal
import sys
import time

from pcg_gazebo.parsers.sdf import create_sdf_element
from pcg_gazebo.parsers.sdf import Material
from pcg_gazebo.simulation.properties.inertial import Inertial
from pcg_gazebo.task_manager import Server, GazeboProxy
 
def create_thrust_stand():
    # base dimensions
    base_length = 0.1
    base_width  = 0.1
    base_height  = 0.2
    base_mass   = 100.0

    # motor dimensions and physics
    motor_length = 0.0275
    motor_radius = 0.027 / 2.0
    motor_mass = 0.048
    motor_damping = 0.0001
    motor_friction = 0.0001

    # add base link
    base_link = create_sdf_element('link')
    base_link.name = 'base_link'
    base_link.add_collision('collision')
    base_link.add_visual('visual')

    # add inertial
    inertial = Inertial.create_inertia('cuboid', mass=base_mass,
        length_x=base_length, length_y=base_width, length_z=base_height).to_sdf()
    base_link.inertial = inertial

    # collision
    collision = create_sdf_element('collision')
    box = create_sdf_element('box')
    box.size = [base_length, base_width, base_height]
    collision.geometry.box = box
    base_link.collisions[0] = collision

    # set visual
    visual = create_sdf_element('visual')
    box = create_sdf_element('box')
    box.size = [base_length, base_width, base_height]
    visual.geometry.box = box
    material = Material.get_gazebo_material('Gazebo/Red')
    visual.material = material
    base_link.visuals[0] = visual

    # add motor link
    motor_link = create_sdf_element('link')
    motor_link.name = 'motor_link'
    motor_link.pose = [(base_length + motor_length)/2 * -1.0, 0, base_height/2 - 2*motor_radius, 0, math.pi/2 * -1.0, 0]
    motor_link.add_collision('collision')
    motor_link.add_visual('visual')
    motor_link.add_visual('prop_visual')

    # add inertial
    inertial = Inertial.create_inertia('solid_cylinder', mass=motor_mass,
        radius=motor_radius, length=motor_length , axis=[0, 0, 1]).to_sdf()
    motor_link.inertial = inertial

    # set collision
    collision = motor_link.get_collision_by_name('collision')
    cylinder = create_sdf_element('cylinder')
    cylinder.radius = motor_radius
    cylinder.length = motor_length
    collision.geometry.cylinder = cylinder

    # set visual
    visual = motor_link.get_visual_by_name('visual')
    visual.geometry.cylinder = cylinder
    material = Material.get_gazebo_material('Gazebo/Orange')
    visual.material = material

    # set prop visual
    prop_visual = motor_link.get_visual_by_name('prop_visual')
    mesh = create_sdf_element('mesh')
    mesh.uri = '/Users/rhys/CloudStation/Projects/GazeboPhysics/meshes/propeller_9x4.7.stl'
    prop_visual.geometry.mesh = mesh
    material = Material.get_gazebo_material('Gazebo/Green')
    prop_visual.material = material

    # add motor joint
    motor_joint = create_sdf_element('joint')
    motor_joint.name = 'motor_joint'
    motor_joint.parent = base_link.name
    motor_joint.child = motor_link.name

    dynamics = create_sdf_element('dynamics')
    dynamics.damping = motor_damping
    dynamics.friction = motor_friction

    axis = create_sdf_element('axis')
    axis.dynamics = dynamics

    # add sensor to joint
    sensor = create_sdf_element('sensor')
    sensor.reset(mode='force_torque')
    sensor.name = 'force_torque_sensor'
    sensor.type = 'force_torque'
    sensor.always_on = True
    sensor.update_rate = 30
    sensor.visualize = True

    motor_joint.axis = axis
    motor_joint.sensor = sensor

    # add imu link (required by the ardupilot plugin)

    imu_link = create_sdf_element('link')
    imu_link.name = 'imu_link'
    imu_link.add_sensor('imu_sensor')
    print(imu_link)

    # add inertial
    imu_inertial = Inertial.create_inertia('cuboid', mass=0.01,
        length_x=0.01, length_y=0.01, length_z=0.01).to_sdf()
    imu_link.inertial = imu_inertial

    # add imu sensor
    imu_sensor = imu_link.get_sensor_by_name('imu_sensor')
    imu_sensor.reset(mode='imu', with_optional_elements=False)
    imu_sensor.name = 'imu_sensor'
    imu_sensor.type = 'imu'
    imu_sensor.pose = [0, 0, 0, math.pi, 0, 0]
    imu_sensor.always_on = True
    imu_sensor.update_rate = 50
    print(imu_sensor)

    # add imu joint
    imu_joint = create_sdf_element('joint')
    imu_joint.name = 'imu_joint'
    imu_joint.parent = base_link.name
    imu_joint.child = imu_link.name

    axis = create_sdf_element('axis')
    imu_joint.axis = axis

    # add lift-drag plugin for prop
    def create_prop_blade_plugin_args(prop_blade_dir):
        plugin_args = dict(
            a0=0.3,
            alpha_stall=1.4,
            cla=4.25,
            cda=0.1,
            cma=0,
            cla_stall=-0.025,
            cda_stall=0,
            cma_stall=0,
            area=0.002,
            air_density=1.2041,
            cp=[0.084 * prop_blade_dir, 0, 0],
            forward=[0, 1 * prop_blade_dir, 0],
            upward=[0, 0, 1],
            link_name=motor_link.name,
        )
        return plugin_args

    prop_blade_1_plugin = create_sdf_element('plugin')
    prop_blade_1_plugin.name = 'prop_blade_1_liftdrag'
    prop_blade_1_plugin.filename = 'libLiftDragPlugin.so'
    prop_blade_1_plugin.value = create_prop_blade_plugin_args(1.0)

    prop_blade_2_plugin = create_sdf_element('plugin')
    prop_blade_2_plugin.name = 'prop_blade_2_liftdrag'
    prop_blade_2_plugin.filename = 'libLiftDragPlugin.so'
    prop_blade_2_plugin.value = create_prop_blade_plugin_args(-1.0)

    # add ardupilot plugin
    ardupilot_plugin_args = dict(
        fdm_addr='127.0.0.1',
        fdm_port_in=9002,
        connectionTimeoutMaxCount=5,
        modelXYZToAirplaneXForwardZDown=[0, 0, 0, math.pi, 0, 0],
        gazeboXYZToNED=[0, 0, 0, math.pi, 0, 0],
        imuName='imu_link::imu_sensor',
    #     control=dict(
    #         attributes=dict(
    #             channel='0'
    #         ),
    #         value=dict(
    #             jointName='steer_joint',
    #             useForce=True,
    #             multiplier=3.141592653,
    #             offset=-0.5,
    #             servo_min=1000,
    #             servo_max=2000,
    #             type='POSITION',
    #             p_gain=10,
    #             i_gain=0.1,
    #             d_gain=0.02,
    #             i_max=1,
    #             i_min=0,
    #             cmd_max=100.0,
    #             cmd_min=-100.0
    #         )
    #     ),
        control=dict(
            attributes=dict(
                channel='2'
            ),
            value=dict(
                jointName='motor_joint',
                useForce=True,
                multiplier=-800,
                offset=0,
                servo_min=1000,
                servo_max=2000,
                type='VELOCITY',
                p_gain=0.007,
                i_gain=0.005,
                d_gain=0.0,
                i_max=0.1,
                i_min=-0.1,
                cmd_max=10.0,
                cmd_min=-10.0
            )
        )
    )

    ardupilot_plugin = create_sdf_element('plugin')
    ardupilot_plugin.name = 'ardupilot_plugin'
    ardupilot_plugin.filename = 'libArduPilotPlugin.so'
    ardupilot_plugin.value = ardupilot_plugin_args

    # create model element
    model = create_sdf_element('model')
    model.name = 'thrust_stand'

    model.add_link(base_link.name, base_link)
    model.add_link(imu_link.name, imu_link)
    model.add_link(motor_link.name, motor_link)

    model.add_joint(motor_joint.name, motor_joint)
    model.add_joint(imu_joint.name, imu_joint)

    model.add_plugin(prop_blade_1_plugin.name, prop_blade_1_plugin)
    model.add_plugin(prop_blade_2_plugin.name, prop_blade_2_plugin)
    model.add_plugin(ardupilot_plugin.name, ardupilot_plugin)

    sdf_model = create_sdf_element('sdf')
    sdf_model.reset(mode='model')
    sdf_model.add_model(model=model)

    return sdf_model

if __name__ == "__main__":

    # create server and start simulation
    # server = Server()
    # server.create_simulation(
    #     'default',
    #     ros_host='macpro2',
    #     ros_port=11311,
    #     gazebo_host='127.0.0.1',
    #     gazebo_port=11345)
    
    # get simulation and run tasks
    simulation = None
    # simulation = server.get_simulation('default')
    # simulation.create_gazebo_empty_world_task()
    # simulation.run_all_tasks()

    # wait for simulation to be ready
    # while not simulation.is_task_running('gazebo'):
    #     time.sleep(0.5)

    # get proxy
    # gazebo_proxy = simulation.get_gazebo_proxy()

    # Alternatively - can launch Gazebo / ROS with
    # 
    # $ rosrun gazebo_ros gazebo 
    gazebo_proxy = GazeboProxy(
        ros_host='macpro2',
        ros_port=11311,
        gazebo_host='127.0.0.1',
        gazebo_port=11345)
    print(gazebo_proxy.ros_config)

    # TODO - remove duplication here
    sdf_model = create_thrust_stand()
    print(sdf_model)

    base_height = 0.2

    model_name = 'thrust_stand'
    gazebo_proxy.spawn_sdf_model(
        robot_namespace=model_name,
        xml=sdf_model.to_xml_as_str(),
        pos=[0, 0, base_height/2 + 0.01],
        rot=[0, 0, 0],
        reference_frame='world')

    # register interrupt signal handler
    def signal_handler(sig, frame):
        print('Ctrl+C: shutting down')
        if simulation is not None:
            simulation.kill_all_tasks()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # spin
    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print('KeyboardInterrupt: shutting down')
        if simulation is not None:
            simulation.kill_all_tasks()
        sys.exit(0)
