#!/bin/bash

set -e

echo "=========================================="
echo "gazebo_ros Source Kurulumu"
echo "ROS 2 Jazzy için"
echo "=========================================="

WORKSPACE_DIR="/home/omer/ur5_ws"
GAZEBO_ROS_WS="$WORKSPACE_DIR/gazebo_ros_ws"

source /opt/ros/jazzy/setup.bash

# Eğer zaten kurulu ise kontrol et
if ros2 pkg list | grep -q gazebo_ros; then
    echo "gazebo_ros zaten kurulu!"
    exit 0
fi

echo ""
echo "1. Gazebo Classic workspace oluşturuluyor..."
mkdir -p "$GAZEBO_ROS_WS/src"
cd "$GAZEBO_ROS_WS/src"

echo ""
echo "2. gazebo_ros_pkgs repository'si klonlanıyor..."
if [ ! -d "gazebo_ros_pkgs" ]; then
    git clone https://github.com/ros-simulation/gazebo_ros_pkgs.git -b ros2
    cd gazebo_ros_pkgs
    
    # Jazzy branch'ini kontrol et
    if git ls-remote --heads origin | grep -q jazzy; then
        git checkout jazzy
    elif git ls-remote --heads origin | grep -q humble; then
        echo "Jazzy branch bulunamadı, Humble branch kullanılıyor (uyumluluk için)"
        git checkout humble
    else
        echo "ros2 branch kullanılıyor"
        git checkout ros2
    fi
fi

echo ""
echo "3. Bağımlılıklar kuruluyor..."
cd "$GAZEBO_ROS_WS"
rosdep update
rosdep install --from-paths src --ignore-src -y -r || echo "Bazı bağımlılıklar kurulamadı, devam ediliyor..."

echo ""
echo "4. Workspace build ediliyor..."
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

echo ""
echo "5. Setup dosyası oluşturuluyor..."
cat > "$WORKSPACE_DIR/source_gazebo_ros.sh" << 'EOF'
#!/bin/bash
source /opt/ros/jazzy/setup.bash
source /home/omer/ur5_ws/gazebo_ros_ws/install/setup.bash
source /home/omer/ur5_ws/install/setup.bash
EOF
chmod +x "$WORKSPACE_DIR/source_gazebo_ros.sh"

echo ""
echo "=========================================="
echo "Kurulum tamamlandı!"
echo "=========================================="
echo ""
echo "gazebo_ros'u kullanmak için:"
echo "  source /home/omer/ur5_ws/source_gazebo_ros.sh"
echo ""

