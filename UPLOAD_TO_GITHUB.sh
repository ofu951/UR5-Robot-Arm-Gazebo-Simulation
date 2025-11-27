#!/bin/bash
# Quick script to upload workspace to GitHub

echo "=========================================="
echo "GitHub Upload Helper Script"
echo "=========================================="

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
fi

# Add all workspace files (excluding build/install/log)
echo "Adding files to git..."
git add .gitignore README.md *.py *.sh *.txt 2>/dev/null

# Show what will be committed
echo ""
echo "Files to be committed:"
git status --short

echo ""
echo "=========================================="
echo "Next steps:"
echo "=========================================="
echo "1. Create a new repository on GitHub"
echo "2. Run these commands:"
echo ""
echo "   git commit -m 'Initial commit: UR5 Gazebo Harmonic workspace'"
echo "   git branch -M main"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo "   git push -u origin main"
echo ""
echo "=========================================="
echo "To include src/ directory changes:"
echo "=========================================="
echo "If you want to upload your modifications to ur_simulation_gazebo:"
echo ""
echo "   cd src/Universal_Robots_ROS2_Gazebo_Simulation/ur_simulation_gazebo"
echo "   git add ."
echo "   git commit -m 'Add Gazebo Harmonic support'"
echo "   git push origin <your-branch>"
echo ""
echo "Or fork the original repository and push your changes there."

