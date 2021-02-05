cmake_minimum_required(VERSION 3.0.2)
project(ardupilot_gazebo_models)

################################################################################
# Dependencies

find_package(gazebo REQUIRED)

################################################################################
# Install

install(DIRECTORY models DESTINATION ${GAZEBO_MODEL_PATH}/..)
install(DIRECTORY worlds DESTINATION ${GAZEBO_MODEL_PATH}/..)
install(DIRECTORY media DESTINATION ${GAZEBO_MEDIA_PATH}/..)

