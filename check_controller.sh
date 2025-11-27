#!/bin/bash
# Controller durumunu kontrol et

source /opt/ros/jazzy/setup.bash
source /home/omer/ur5_ws/install/setup.bash

echo "=== Controller Service'leri ==="
ros2 service list | grep controller

echo ""
echo "=== Action Server'lar ==="
ros2 action list | grep trajectory

echo ""
echo "=== Joint States ==="
timeout 2 ros2 topic echo /joint_states --once 2>&1 | head -15

echo ""
echo "=== Controller Manager Node'ları ==="
ros2 node list | grep controller

