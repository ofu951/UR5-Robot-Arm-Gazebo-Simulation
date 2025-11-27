# Setup Instructions for Cloning This Repository

## Quick Setup

After cloning this repository, follow these steps to build and use it:

### 1. Clone the Repository

```bash
git clone git@github.com:YOUR_USERNAME/UR5-Robot-Arm-Gazebo-Simulation.git
cd UR5-Robot-Arm-Gazebo-Simulation
```

### 2. Install Dependencies

```bash
# Install ROS 2 Jazzy packages
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

# Install Gazebo Harmonic
sudo curl -sSL https://get.gazebosim.org | sh
```

### 3. Get Source Packages

If `src/` directory is not included in the repository, you need to clone the source packages:

```bash
mkdir -p src
cd src

# Clone Universal Robots packages
git clone https://github.com/UniversalRobots/Universal_Robots_ROS2_Description.git
git clone https://github.com/UniversalRobots/Universal_Robots_ROS2_Gazebo_Simulation.git

# If you have modifications, apply them to ur_simulation_gazebo
cd Universal_Robots_ROS2_Gazebo_Simulation/ur_simulation_gazebo
# Copy your modified files here (urdf/ros2_control_gazebo.xacro, launch/ur_sim_control.launch.py, etc.)
```

### 4. Build the Workspace

```bash
cd ~/UR5-Robot-Arm-Gazebo-Simulation  # or your workspace path
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

### 5. Run the Simulation

```bash
ros2 launch ur_simulation_gazebo ur_sim_control.launch.py ur_type:=ur5
```

## Why build/ and install/ are not included?

- `build/` and `install/` directories are build artifacts
- They are system-specific and should be generated on each machine
- Including them would make the repository unnecessarily large
- Each user should build the workspace on their own system

## Including src/ directory

If you want to include the `src/` directory in the repository:

1. The source packages contain their own `.git` directories (nested repositories)
2. You can either:
   - Remove the `.git` directories temporarily and commit the source code
   - Use git submodules (recommended for maintaining links to original repos)
   - Fork the original repositories and include your modifications there

See `ADD_SRC_DIRECTORY.sh` script for help with including src/ directory.

