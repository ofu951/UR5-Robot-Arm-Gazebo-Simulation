#!/bin/bash

# ROS 2 Jazzy için gerekli paketleri kur
echo "ROS 2 Jazzy bağımlılıklarını kuruyorum..."

sudo apt update

# Temel ROS 2 paketleri
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
    ros-jazzy-launch-ros

# Gazebo Classic için paketler (Jazzy için mevcut olabilir veya olmayabilir)
sudo apt install -y \
    ros-jazzy-gazebo-ros \
    ros-jazzy-gazebo-ros2-control \
    gazebo \
    libgazebo-dev || echo "Gazebo Classic paketleri bulunamadı, alternatif kontrol ediliyor..."

# Eğer yukarıdaki paketler yoksa, source'den kurulum gerekebilir
if ! ros2 pkg list | grep -q gazebo_ros; then
    echo "gazebo_ros bulunamadı. Source'den kurulum gerekebilir."
    echo "Alternatif olarak Gazebo (Ignition) kullanılabilir."
fi

echo "Kurulum tamamlandı!"

