# GitHub Upload Instructions

## Option 1: Upload Only Workspace Files (Recommended)

This option uploads only your custom scripts and configuration files, excluding the source packages.

```bash
cd ~/ur5_ws
git add .
git commit -m "Initial commit: UR5 Gazebo Harmonic simulation workspace"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## Option 2: Upload Everything Including Source Packages

If you want to include the modified source packages:

1. First, commit changes in the source packages:
```bash
cd ~/ur5_ws/src/Universal_Robots_ROS2_Gazebo_Simulation/ur_simulation_gazebo
git add .
git commit -m "Add Gazebo Harmonic support and ros2_control integration"
```

2. Then add them as submodules or copy them:
```bash
cd ~/ur5_ws
# Remove .gitignore entries for src/ and gazebo_ros_ws/
# Then add everything
git add .
git commit -m "Initial commit with source packages"
```

## Quick Setup

```bash
# Initialize and commit
cd ~/ur5_ws
git add .
git commit -m "UR5 Gazebo Harmonic simulation workspace"

# Create GitHub repository first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

