# Quick Start Guide

## Prerequisites

- Ubuntu 24.04
- ROS 2 Jazzy installed and sourced
- Git and SSH keys configured for GitHub

## Installation Steps

```bash
# 1. Clone the repository
git clone git@github.com:YOUR_USERNAME/UR5-Robot-Arm-Gazebo-Simulation.git
cd UR5-Robot-Arm-Gazebo-Simulation

# 2. Source ROS 2 Jazzy
source /opt/ros/jazzy/setup.bash

# 3. Run the setup script (requires sudo for package installation)
./setup_workspace.sh

# 4. Source the workspace
source install/setup.bash

# 5. Launch the simulation
ros2 launch ur_simulation_gazebo ur_sim_control.launch.py ur_type:=ur5
```

## What the Setup Script Does

1. **Installs Dependencies**: All required ROS 2 packages and Gazebo Harmonic
2. **Clones Source Packages**: Universal Robots ROS 2 packages from GitHub
3. **Applies Modifications**: Adds Gazebo Harmonic support (ros2_control plugin, launch file updates)
4. **Builds Workspace**: Compiles the workspace with your modifications

## Troubleshooting

### Setup script fails with "ROS 2 is not sourced"
Make sure you run `source /opt/ros/jazzy/setup.bash` before running the setup script.

### Build fails
- Make sure all dependencies are installed
- Try: `colcon build --symlink-install --packages-select ur_description ur_simulation_gazebo`

### Controller not starting
- Wait a few seconds after launching the simulation
- Check: `ros2 service call /controller_manager/list_controllers controller_manager_msgs/srv/ListControllers`

### Robot joints falling
- This indicates the ros2_control plugin is not loaded properly
- Make sure `gz-ros2-control` package is installed
- Check Gazebo logs for plugin loading errors

## Next Steps

After the simulation is running, you can control the robot using:

```bash
# Move to joint angles
python3 move_ur5.py 0.5 -1.0 1.5 -1.0 1.5 0.0 6.0

# Move to 3D point
python3 move_ur5.py 0.5 0.0 0.8 6.0
```

