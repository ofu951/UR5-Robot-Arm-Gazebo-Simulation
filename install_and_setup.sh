#!/bin/bash

set -e

echo "=========================================="
echo "UR5 Gazebo Simülasyon Kurulum Scripti"
echo "ROS 2 Jazzy - Ubuntu 24.04"
echo "=========================================="

# ROS 2 Jazzy source
source /opt/ros/jazzy/setup.bash

echo ""
echo "1. Sistem güncellemesi yapılıyor..."
sudo apt update

echo ""
echo "2. Temel ROS 2 paketleri kuruluyor..."
sudo apt install -y \
    ros-jazzy-controller-manager \
    ros-jazzy-joint-state-broadcaster \
    ros-jazzy-joint-trajectory-controller \
    ros-jazzy-velocity-controllers \
    ros-jazzy-position-controllers \
    ros-jazzy-ur-controllers \
    ros-jazzy-ur-moveit-config \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-rviz2 \
    ros-jazzy-xacro \
    ros-jazzy-urdf \
    ros-jazzy-launch \
    ros-jazzy-launch-ros \
    ros-jazzy-gz-ros2-control \
    python3-colcon-common-extensions

echo ""
echo "3. Gazebo Harmonic kuruluyor..."
if ! command -v gz &> /dev/null; then
    echo "Gazebo Harmonic kurulumu başlatılıyor..."
    sudo curl -sSL https://get.gazebosim.org | sh
else
    echo "Gazebo zaten kurulu: $(gz sim --version 2>/dev/null || echo 'version bilgisi alınamadı')"
fi

echo ""
echo "4. Gazebo Classic için gerekli paketler kontrol ediliyor..."
# Gazebo Classic için source'dan kurulum gerekebilir
if ! ros2 pkg list | grep -q gazebo_ros; then
    echo "gazebo_ros bulunamadı. Source'dan kurulum deneniyor..."
    echo "Not: Gazebo Classic end-of-life olduğu için yeni Gazebo (Harmonic) kullanılması önerilir."
    
    # Alternatif: Gazebo Classic'i source'dan kurmayı dene
    WORKSPACE_DIR="/home/omer/ur5_ws"
    GAZEBO_ROS_WS="$WORKSPACE_DIR/gazebo_ros_ws"
    
    if [ ! -d "$GAZEBO_ROS_WS" ]; then
        echo "Gazebo Classic source workspace oluşturuluyor..."
        mkdir -p "$GAZEBO_ROS_WS/src"
        cd "$GAZEBO_ROS_WS/src"
        
        # Gazebo Classic ROS 2 paketlerini klonla (eğer mevcut ise)
        if [ ! -d "gazebo_ros_pkgs" ]; then
            echo "gazebo_ros_pkgs repository'si klonlanıyor..."
            git clone https://github.com/ros-simulation/gazebo_ros_pkgs.git -b ros2
            cd gazebo_ros_pkgs
            git checkout $(git tag | grep -E "^(ros2|jazzy)" | tail -1 || echo "ros2")
        fi
    fi
fi

echo ""
echo "5. Workspace build ediliyor..."
cd /home/omer/ur5_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install

echo ""
echo "=========================================="
echo "Kurulum tamamlandı!"
echo "=========================================="
echo ""
echo "Simülasyonu çalıştırmak için:"
echo "  source /opt/ros/jazzy/setup.bash"
echo "  source /home/omer/ur5_ws/install/setup.bash"
echo "  ros2 launch ur_simulation_gazebo ur_sim_control.launch.py ur_type:=ur5"
echo ""

