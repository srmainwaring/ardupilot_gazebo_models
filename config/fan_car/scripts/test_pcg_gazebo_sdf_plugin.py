#!/usr/bin/env python3

'''
Use pcg_gazebo to parse sdf plugins containing repeated elements and lists
'''

from pcg_gazebo.parsers.sdf import create_sdf_element
from pcg_gazebo.parsers.sdf import Plugin


def test_lists_1():
    print('test_lists_1\n')
    plugin_args = dict(
        xyz=[1, 2, 3],
        rpy=[0.1, 0.2, 0.3]
    )

    plugin = create_sdf_element('plugin')
    plugin.name = 'plugin'
    plugin.filename = 'libPlugin.so'
    plugin.from_dict(plugin_args)    
    print(plugin)

def test_lists_2():
    print('test_lists_2\n')
    plugin_args = dict(
        pose=dict(
            attributes=dict(),
            value=dict(
                xyz=[1.1, 2.2, 3.3],
                rpy=[0.1, 0.2, 0.3]
            )
        ),
        twist=dict(
            attributes=dict(),
            value=dict(
                linear=[5.5, 6.6, 7.7],
                angular=[1.1, 1.2, 1.3]
            )
        )
    )

    plugin = create_sdf_element('plugin')
    plugin.name = 'plugin'
    plugin.filename = 'libPlugin.so'
    plugin.from_dict(plugin_args)    
    print(plugin)

def test_repeated_elements():
    print('test_repeated_elements\n')
    plugin_args = dict(
        control=list([
            dict(
                attributes=dict(
                    channel="0"
                ),
                value=dict(
                    jointName='steer_joint',
                    useForce=1
                )
            ),
            dict(
                attributes=dict(
                    channel="2"
                ),
                value=dict(
                    jointName='motor_joint',
                    useForce=1
                )
            )
        ])
    )

    plugin = create_sdf_element('plugin')
    plugin.name = 'plugin'
    plugin.filename = 'libPlugin.so'
    plugin.from_dict(plugin_args)    
    print(plugin)

if __name__ == '__main__':
    print('test_pcg_gazebo_sdf_plugin\n')

    test_lists_1()
    test_lists_2()
    test_repeated_elements()
