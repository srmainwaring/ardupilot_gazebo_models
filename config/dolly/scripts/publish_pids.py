#!/usr/bin/env python3

'''
Publish PID messages

This script uses a fork of pygazebo to publish PID messages
so that joint control settings may be updated dynamically.

Requirements:
-------------

Install pygazebo from the `ci-group` fork. This supports Gazebo11 and Python3.

- pygazebo [ci-group/pygazebo](https://github.com/ci-group/pygazebo)

Notes:
------

There are two pub/sub systems operating in Gazebo. The legacy Gazebo transport
system and the successor ignition transport system.

pygazebo supports the legacy transport and message definitions. This means that
a Gazebo plugin will need to initialise a `gazebo:transport::NodePtr` and
retain a gazebo::transport::SubscriberPtr` for each subscription.
'''

import asyncio
import pygazebo
from pygazebo.msg.joint_pb2 import Joint
from pygazebo.msg.joint_cmd_pb2 import JointCmd
from pygazebo.msg.packet_pb2 import Packet
from pygazebo.msg.poses_stamped_pb2 import PosesStamped
from pygazebo.msg.subscribe_pb2 import Subscribe
from pygazebo.msg.pid_pb2 import PID

def pose_info_cb(data):
    pose = PosesStamped.FromString(data)
    print("pose: {}".format(pose))

def joint_cb(data):
    joint = Joint.FromString(data)
    print("joint: {}".format(joint))

async def main_loop():
    manager = await pygazebo.connect()

    # publishers
    publishers = []
    messages = []

    # topics:
    # /dolly_ball_castor_ardupilot/dolly_ball_castor/back_motor_joint/pid
    # /dolly_ardupilot/dolly/back_steer_rotor_joint/pid
    
    if False:
        publisher = await manager.advertise(
            '/gazebo/dolly_world/dolly_ardupilot/dolly/back_motor_joint/pid',
            'gazebo.msgs.PID')
        
        message = PID()
        message.p_gain = 0.005
        message.i_gain = 0.01
        message.d_gain = 0.0
        message.i_max  = 0.1
        message.i_min  = -0.1
        message.limit  = 5.0

        publishers.append(publisher)
        messages.append(message)

    if False:
        publisher = await manager.advertise(
            '/gazebo/dolly_world/dolly_ball_castor_ardupilot/dolly_ball_castor/back_steer_rotor_joint/pid',
            'gazebo.msgs.PID')
        
        message = PID()
        message.p_gain = 10.0
        message.i_gain = 0.1
        message.d_gain = 0.02
        message.i_max  = 1.0
        message.i_min  = -1.0
        message.limit  = 100.0

        publishers.append(publisher)
        messages.append(message)

    if True:
        publisher = await manager.advertise(
            '/gazebo/default/motor_joint/pid',
            'gazebo.msgs.PID')
        
        message = PID()
        message.p_gain = 0.007
        message.i_gain = 0.005
        message.d_gain = 0.0
        message.i_max  = 0.1
        message.i_min  = -0.1
        message.limit  = 10.0

        publishers.append(publisher)
        messages.append(message)


    # subscribers
    # subscriber = await manager.subscribe(
    #     topic_prefix + '/pose/info',
    #     'gazebo.msgs.PosesStamped',
    #     pose_info_cb)

    # subscriber = await manager.subscribe(
    #     topic_prefix + '/joint',
    #     'gazebo.msgs.Joint',
    #     joint_cb)

    # main loop
    while True:
        for i in range(len(publishers)):
            await publishers[i].publish(messages[i])
        await asyncio.sleep(1.0)

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop())
