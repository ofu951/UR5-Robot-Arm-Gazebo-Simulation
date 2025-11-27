# UR5 Robot Simulation with Gazebo Harmonic

This repository contains a ROS 2 Jazzy workspace for simulating Universal Robots UR5 manipulator in Gazebo Harmonic (Ignition Gazebo). The simulation includes robot control via `ros2_control` framework with cubic trajectory planning.

## Requirements

- **OS**: Ubuntu 24.04
- **ROS**: ROS 2 Jazzy
- **Gazebo**: Gazebo Harmonic (Ignition Gazebo)
- **Python**: Python 3.12+

## Installation

### 1. Install ROS 2 Jazzy

Follow the official [ROS 2 Jazzy installation guide](https://docs.ros.org/en/jazzy/Installation.html).

### 2. Install Required ROS 2 Packages

```bash
sudo apt update
sudo apt install -y \
    ros-jazzy-controller-manager \
    ros-jazzy-joint-state-broadcaster \
    ros-jazzy-joint-trajectory-controller \
    ros-jazzy-gz-ros2-control \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ur-controllers \
    ros-jazzy-ur-description \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-rviz2 \
    ros-jazzy-xacro
```

### 3. Install Gazebo Harmonic

```bash
sudo curl -sSL https://get.gazebosim.org | sh
```

### 4. Build the Workspace

```bash
cd ~/ur5_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Usage

### Launch Simulation

```bash
source /opt/ros/jazzy/setup.bash
source ~/ur5_ws/install/setup.bash
ros2 launch ur_simulation_gazebo ur_sim_control.launch.py ur_type:=ur5
```

### Control the Robot

The workspace includes a Python script for controlling the robot with cubic trajectories:

**Move to joint angles:**
```bash
python3 move_ur5.py <j1> <j2> <j3> <j4> <j5> <j6> <duration>
```

**Move to 3D point:**
```bash
python3 move_ur5.py <x> <y> <z> <duration>
```

Example:
```bash
python3 move_ur5.py 0.5 -1.0 1.5 -1.0 1.5 0.0 6.0
```

## Features

- **Gazebo Harmonic Integration**: Uses `ros_gz_sim` for simulation
- **ros2_control Support**: Full hardware interface integration
- **Cubic Trajectory Planning**: Smooth motion planning for robot joints
- **Inverse Kinematics**: Move robot to 3D Cartesian coordinates
- **Table Support**: Robot spawns on a stable table surface

## Supported Robot Types

- ur3, ur3e
- ur5, ur5e
- ur7e
- ur10, ur10e
- ur12e, ur16e
- ur20, ur30

## Troubleshooting

### Controller Not Starting

If the controller manager service is not available:

```bash
ros2 service call /controller_manager/list_controllers controller_manager_msgs/srv/ListControllers
```

### Action Server Not Found

Ensure the simulation is running and wait a few seconds for controllers to initialize:

```bash
ros2 action list | grep trajectory
```

### Robot Joints Falling

This usually indicates that the `gz_ros2_control` plugin is not properly loaded. The launch file automatically sets the `GZ_SIM_SYSTEM_PLUGIN_PATH` environment variable to include the plugin path.

## License

BSD-3-Clause

## Acknowledgments

This workspace is based on the [Universal Robots ROS 2 Gazebo Simulation](https://github.com/UniversalRobots/Universal_Robots_ROS2_Gazebo_Simulation) repository, adapted for Gazebo Harmonic and ROS 2 Jazzy.

