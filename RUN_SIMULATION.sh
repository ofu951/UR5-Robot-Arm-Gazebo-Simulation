#!/bin/bash

# UR5 Gazebo Simülasyonu Çalıştırma Scripti

echo "=========================================="
echo "UR5 Gazebo Simülasyonu Başlatılıyor"
echo "=========================================="

# ROS 2 Jazzy source
source /opt/ros/jazzy/setup.bash

# gazebo_ros varsa source et
if [ -f "/home/omer/ur5_ws/source_gazebo_ros.sh" ]; then
    echo "gazebo_ros source ediliyor..."
    source /home/omer/ur5_ws/source_gazebo_ros.sh
else
    # Sadece workspace source et
    source /home/omer/ur5_ws/install/setup.bash
fi

# UR tipi kontrolü
UR_TYPE=${1:-ur5}

echo ""
echo "UR Robot Tipi: $UR_TYPE"
echo ""

# Simülasyonu başlat
ros2 launch ur_simulation_gazebo ur_sim_control.launch.py ur_type:=$UR_TYPE
