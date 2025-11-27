#!/bin/bash
# Complete workspace setup script
# This script clones required packages and applies modifications for Gazebo Harmonic

set -e

echo "=========================================="
echo "UR5 Gazebo Harmonic Workspace Setup"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if ROS 2 Jazzy is sourced
if [ -z "$ROS_DISTRO" ]; then
    echo "ERROR: ROS 2 is not sourced. Please run:"
    echo "  source /opt/ros/jazzy/setup.bash"
    exit 1
fi

if [ "$ROS_DISTRO" != "jazzy" ]; then
    echo "WARNING: ROS_DISTRO is '$ROS_DISTRO', expected 'jazzy'"
fi

echo ""
echo "Step 1: Installing dependencies..."
echo "-----------------------------------"
sudo apt update
sudo apt install -y \
    ros-jazzy-controller-manager \
    ros-jazzy-joint-state-broadcaster \
    ros-jazzy-joint-trajectory-controller \
    ros-jazzy-gz-ros2-control \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-ur-controllers \
    ros-jazzy-ur-description \
    ros-jazzy-ur-moveit-config \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-rviz2 \
    ros-jazzy-xacro \
    python3-colcon-common-extensions || true

# Install Gazebo Harmonic if not installed
if ! command -v gz &> /dev/null; then
    echo ""
    echo "Step 2: Installing Gazebo Harmonic..."
    echo "--------------------------------------"
    sudo curl -sSL https://get.gazebosim.org | sh
else
    echo ""
    echo "Step 2: Gazebo Harmonic already installed"
    echo "--------------------------------------"
fi

echo ""
echo "Step 3: Cloning source packages..."
echo "-----------------------------------"
mkdir -p src
cd src

# Clone Universal Robots packages if they don't exist
if [ ! -d "Universal_Robots_ROS2_Description" ]; then
    echo "Cloning Universal_Robots_ROS2_Description..."
    git clone https://github.com/UniversalRobots/Universal_Robots_ROS2_Description.git
else
    echo "Universal_Robots_ROS2_Description already exists, skipping..."
fi

if [ ! -d "Universal_Robots_ROS2_Gazebo_Simulation" ]; then
    echo "Cloning Universal_Robots_ROS2_Gazebo_Simulation..."
    git clone https://github.com/UniversalRobots/Universal_Robots_ROS2_Gazebo_Simulation.git
else
    echo "Universal_Robots_ROS2_Gazebo_Simulation already exists, skipping..."
fi

cd "$SCRIPT_DIR"

echo ""
echo "Step 4: Applying modifications for Gazebo Harmonic..."
echo "------------------------------------------------------"

# Apply modifications to ur_simulation_gazebo
PACKAGE_DIR="src/Universal_Robots_ROS2_Gazebo_Simulation/ur_simulation_gazebo"

# Create urdf directory if it doesn't exist
mkdir -p "$PACKAGE_DIR/urdf"

# Copy ros2_control_gazebo.xacro
echo "  - Adding ros2_control_gazebo.xacro..."
cp patches/urdf/ros2_control_gazebo.xacro "$PACKAGE_DIR/urdf/"

# Update CMakeLists.txt to install urdf directory
echo "  - Updating CMakeLists.txt..."
if ! grep -q "install(DIRECTORY config launch urdf" "$PACKAGE_DIR/CMakeLists.txt"; then
    sed -i 's/install(DIRECTORY config launch/install(DIRECTORY config launch urdf/' "$PACKAGE_DIR/CMakeLists.txt"
fi

# Update package.xml to include gz-ros2-control
echo "  - Updating package.xml..."
if ! grep -q "gz-ros2-control" "$PACKAGE_DIR/package.xml"; then
    # Add exec_depend for gz-ros2-control after controller_manager
    sed -i '/<exec_depend>controller_manager<\/exec_depend>/a\  <exec_depend>gz-ros2-control<\/exec_depend>' "$PACKAGE_DIR/package.xml"
fi

# Copy modified launch file
echo "  - Updating launch file..."
cp patches/launch/ur_sim_control.launch.py "$PACKAGE_DIR/launch/"

echo ""
echo "Step 5: Building workspace..."
echo "------------------------------"
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select ur_description ur_simulation_gazebo

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To use the workspace, run:"
echo "  source install/setup.bash"
echo ""
echo "To launch the simulation:"
echo "  ros2 launch ur_simulation_gazebo ur_sim_control.launch.py ur_type:=ur5"
echo ""

