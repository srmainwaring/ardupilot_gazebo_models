#!/usr/bin/env python3

'''
Use pcg_gazebo sdf physics (for joints)
'''

from pcg_gazebo.parsers.sdf import create_sdf_element
from pcg_gazebo.parsers.sdf import Physics, ODE


def test_joint_physics():
    print('test_joint_physics\n')

    #--------------------------------------------------------------
    # limit element for joints
    limit = create_sdf_element('limit')

    # without optional elements
    limit.reset(mode='joint', with_optional_elements=False)
    print(limit)

    # with optional elements
    limit.reset(mode='joint', with_optional_elements=True)
    print(limit)

    # these are the defaults applied when converting urdf to sdf
    limit.cfm = 0.0
    limit.erp = 0.2
    print(limit)

    #--------------------------------------------------------------
    # ode element for joints
    ode = create_sdf_element('ode')
    
    # without optional elements
    ode.reset(mode='joint', with_optional_elements=False)
    print(ode)

    # with optional elements
    ode.reset(mode='joint', with_optional_elements=True)
    print(ode)

    # with limit element set
    ode.reset(mode='joint', with_optional_elements=False)
    ode.limit = limit
    print(ode)

    #--------------------------------------------------------------
    # physics element for joints
    physics = create_sdf_element('physics')

    # without optional elements
    physics.reset(mode='joint', with_optional_elements=False)
    print(physics)

    # with optional elements
    physics.reset(mode='joint', with_optional_elements=True)
    print(physics)

    # with ode element set
    ode.reset(mode='joint', with_optional_elements=False)
    # this fails because the settor for ode is not correct
    # physics.ode = ode
    # print(physics)

    # work around: remove unwanted elements
    physics.rm_child('provide_feedback')
    physics.rm_child('simbody')
    physics.ode.rm_child('provide_feedback')
    physics.ode.rm_child('cfm_damping')
    physics.ode.rm_child('cfm')
    physics.ode.rm_child('erp')
    physics.ode.limit = limit
    print(physics)


def  test_collision_friction():
    print('test_collision_friction\n')

    #--------------------------------------------------------------
    # ode element for joints
    friction = create_sdf_element('friction')
    
    # with optional elements
    friction.reset(mode='surface', with_optional_elements=True)
    print(friction)

    # remove elements
    friction.rm_child('bullet')
    friction.rm_child('torsional')
    print(friction)

def  test_collision_ode():
    print('test_collision_ode\n')

    #--------------------------------------------------------------
    # ode element for joints
    ode = create_sdf_element('ode')
    
    # with optional elemaents
    ode.reset(mode='collision', with_optional_elements=True)
    print(ode)

    # remove elements
    ode.rm_child('fdir1')
    ode.rm_child('slip1')
    ode.rm_child('slip2')
    ode.mu = 1.0
    ode.mu2 = 1.0
    print(ode)


if __name__ == '__main__':
    print('test_pcg_gazebo_sdf_joint_physics\n')

    # test_collision_friction()
    test_collision_ode()
    # test_joint_physics()
