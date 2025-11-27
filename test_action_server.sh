#!/bin/bash
# Action server'ı test et
source /opt/ros/jazzy/setup.bash
source /home/omer/ur5_ws/install/setup.bash

echo "=== Action Server Listesi ==="
ros2 action list

echo ""
echo "=== Joint States ==="
timeout 2 ros2 topic echo /joint_states --once 2>&1 | head -10

echo ""
echo "=== Controller Topics ==="
ros2 topic list | grep -i trajectory
