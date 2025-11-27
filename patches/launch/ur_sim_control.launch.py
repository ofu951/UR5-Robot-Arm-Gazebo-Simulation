# Copyright (c) 2021 Stogl Robotics Consulting UG (haftungsbeschränkt)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the {copyright_holder} nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Author: Denis Stogl

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    RegisterEventHandler,
    ExecuteProcess,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os
import tempfile


def launch_setup(context, *args, **kwargs):
    import subprocess
    import xml.etree.ElementTree as ET

    # Initialize Arguments
    ur_type = LaunchConfiguration("ur_type")
    safety_limits = LaunchConfiguration("safety_limits")
    safety_pos_margin = LaunchConfiguration("safety_pos_margin")
    safety_k_position = LaunchConfiguration("safety_k_position")
    # General arguments
    runtime_config_package = LaunchConfiguration("runtime_config_package")
    controllers_file = LaunchConfiguration("controllers_file")
    initial_positions_file = LaunchConfiguration("initial_positions_file")
    description_package = LaunchConfiguration("description_package")
    description_file = LaunchConfiguration("description_file")
    description_file = LaunchConfiguration("description_file")
    prefix = LaunchConfiguration("prefix")
    start_joint_controller = LaunchConfiguration("start_joint_controller")
    initial_joint_controller = LaunchConfiguration("initial_joint_controller")
    launch_rviz = LaunchConfiguration("launch_rviz")
    gazebo_gui = LaunchConfiguration("gazebo_gui")

    initial_joint_controllers = PathJoinSubstitution(
        [FindPackageShare(runtime_config_package), "config", controllers_file]
    )

    initial_positions_file_abs = PathJoinSubstitution(
        [FindPackageShare(runtime_config_package), "config", initial_positions_file]
    )

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare(description_package), "rviz", "view_robot.rviz"]
    )

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare(description_package), "urdf", description_file]
            ),
            " ",
            "safety_limits:=",
            safety_limits,
            " ",
            "safety_pos_margin:=",
            safety_pos_margin,
            " ",
            "safety_k_position:=",
            safety_k_position,
            " ",
            "name:=",
            "ur",
            " ",
            "ur_type:=",
            ur_type,
            " ",
            "prefix:=",
            prefix,
            " ",
            "sim_gazebo:=true",
            " ",
            "simulation_controllers:=",
            initial_joint_controllers,
            " ",
            "initial_positions_file:=",
            initial_positions_file_abs,
        ]
    )
    
    # Gazebo için ros2_control ekle - iki xacro çıktısını birleştir
    # Python ile robot_description oluştur
    def create_robot_description_with_ros2_control():
        import subprocess
        import xml.etree.ElementTree as ET
        from ament_index_python.packages import get_package_share_directory
        
        # Path'leri al
        desc_pkg = description_package.perform(context)
        desc_file = description_file.perform(context)
        urdf_path = os.path.join(get_package_share_directory(desc_pkg), "urdf", desc_file)
        
        ros2_control_path = os.path.join(
            get_package_share_directory("ur_simulation_gazebo"),
            "urdf",
            "ros2_control_gazebo.xacro"
        )
        
        init_pos_file = initial_positions_file_abs.perform(context)
        
        # URDF'i oluştur
        urdf_cmd = [
            "xacro",
            urdf_path,
            f"safety_limits:={safety_limits.perform(context)}",
            f"safety_pos_margin:={safety_pos_margin.perform(context)}",
            f"safety_k_position:={safety_k_position.perform(context)}",
            "name:=ur",
            f"ur_type:={ur_type.perform(context)}",
            f"prefix:={prefix.perform(context)}",
            "sim_gazebo:=true",
            f"simulation_controllers:={initial_joint_controllers.perform(context)}",
            f"initial_positions_file:={init_pos_file}",
        ]
        
        # Ros2_control xacro'sunu oluştur
        ros2_control_cmd = [
            "xacro",
            ros2_control_path,
            f"initial_positions_file:={init_pos_file}",
        ]
        
        # Her iki xacro'yu çalıştır
        try:
            urdf_result = subprocess.run(urdf_cmd, capture_output=True, text=True, check=True)
            ros2_control_result = subprocess.run(ros2_control_cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Xacro hatası: {e.stderr}")
        
        # İki XML'i birleştir
        urdf_root = ET.fromstring(urdf_result.stdout)
        ros2_control_root = ET.fromstring(ros2_control_result.stdout)
        
        # ros2_control elementini URDF'e ekle
        for element in ros2_control_root:
            if element.tag == "ros2_control":
                urdf_root.append(element)
        
        return ET.tostring(urdf_root, encoding="unicode")
    
    # Robot description'ı oluştur
    robot_description_str = create_robot_description_with_ros2_control()
    robot_description = {"robot_description": robot_description_str}

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[{"use_sim_time": True}, robot_description],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
        condition=IfCondition(launch_rviz),
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    # Delay rviz start after `joint_state_broadcaster`
    delay_rviz_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[rviz_node],
        ),
        condition=IfCondition(launch_rviz),
    )

    # There may be other controllers of the joints, but this is the initially-started one
    initial_joint_controller_spawner_started = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[initial_joint_controller, "-c", "/controller_manager"],
        condition=IfCondition(start_joint_controller),
    )
    initial_joint_controller_spawner_stopped = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[initial_joint_controller, "-c", "/controller_manager", "--stopped"],
        condition=UnlessCondition(start_joint_controller),
    )

    # Gazebo nodes - Using ros_gz_sim for Gazebo Harmonic
    # Build gazebo args based on GUI setting
    gazebo_args = LaunchConfiguration("gz_args")
    
    # Gazebo'nun ros2_control plugin'ini bulabilmesi için environment variable'ları ayarla
    from ament_index_python.packages import get_package_share_directory
    gz_ros2_control_plugin_path = os.path.join(
        get_package_share_directory("gz_ros2_control"),
        "..", "..", "lib"
    )
    gz_ros2_control_plugin_path = os.path.abspath(gz_ros2_control_plugin_path)
    
    # GZ_SIM_SYSTEM_PLUGIN_PATH environment variable'ını ayarla
    current_plugin_path = os.environ.get("GZ_SIM_SYSTEM_PLUGIN_PATH", "")
    if current_plugin_path:
        new_plugin_path = f"{current_plugin_path}:{gz_ros2_control_plugin_path}"
    else:
        new_plugin_path = gz_ros2_control_plugin_path
    
    # Environment variable'ı ayarla (tüm child process'ler için)
    os.environ["GZ_SIM_SYSTEM_PLUGIN_PATH"] = new_plugin_path
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("ros_gz_sim"), "/launch", "/gz_sim.launch.py"]
        ),
        launch_arguments={
            "gz_args": "",
            "gz_version": "8",
        }.items(),
    )

    # Masa SDF tanımı
    table_sdf_string = (
        '<?xml version="1.0"?>'
        '<sdf version="1.7">'
        '<model name="table">'
        '<static>true</static>'
        '<link name="link">'
        '<collision name="collision">'
        '<geometry><box><size>1.2 0.8 0.05</size></box></geometry>'
        '</collision>'
        '<visual name="visual">'
        '<geometry><box><size>1.2 0.8 0.05</size></box></geometry>'
        '<material><ambient>0.8 0.8 0.8 1</ambient><diffuse>0.8 0.8 0.8 1</diffuse></material>'
        '</visual>'
        '<inertial><mass>50.0</mass><inertia><ixx>6.67</ixx><iyy>8.33</iyy><izz>8.33</izz></inertia></inertial>'
        '</link>'
        '</model>'
        '</sdf>'
    )
    
    # Masa spawn node - önce masayı spawn et
    spawn_table = Node(
        package="ros_gz_sim",
        executable="create",
        name="spawn_table",
        arguments=[
            "-world", "default",
            "-string", table_sdf_string,
            "-name", "table",
            "-x", "0.0",
            "-y", "0.0",
            "-z", "0.4",  # Masa yüksekliği/2 (0.05m kalınlık, merkez 0.4m = 0.8m yükseklik)
        ],
        output="screen",
    )
    
    # Spawn robot using ros_gz_sim - masanın üzerine yerleştir
    # Masa yüksekliği: 0.8m (z=0.4 + 0.05/2 = 0.425m üst yüzey)
    # Robot base yüksekliği: ~0.1m
    # Toplam z: 0.425 + 0.05 = 0.475m (masa üst yüzeyi + robot base yarısı)
    gazebo_spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("ros_gz_sim"), "/launch", "/gz_spawn_model.launch.py"]
        ),
        launch_arguments={
            "topic": "robot_description",
            "entity_name": "ur",
            "x": "0.0",
            "y": "0.0",
            "z": "0.475",  # Masa üst yüzeyine yerleştir (0.425m masa üst + 0.05m robot base yarısı)
        }.items(),
    )

    nodes_to_start = [
        robot_state_publisher_node,
        gazebo,
        spawn_table,  # Önce masayı spawn et
        gazebo_spawn_robot,  # Sonra robotu masanın üzerine
        joint_state_broadcaster_spawner,
        delay_rviz_after_joint_state_broadcaster_spawner,
        initial_joint_controller_spawner_stopped,
        initial_joint_controller_spawner_started,
    ]

    return nodes_to_start


def generate_launch_description():
    # Gazebo'nun ros2_control plugin'ini bulabilmesi için environment variable'ları ayarla
    from ament_index_python.packages import get_package_share_directory
    gz_ros2_control_plugin_path = os.path.join(
        get_package_share_directory("gz_ros2_control"),
        "..", "..", "lib"
    )
    gz_ros2_control_plugin_path = os.path.abspath(gz_ros2_control_plugin_path)
    
    # GZ_SIM_SYSTEM_PLUGIN_PATH environment variable'ını ayarla
    current_plugin_path = os.environ.get("GZ_SIM_SYSTEM_PLUGIN_PATH", "")
    if current_plugin_path:
        new_plugin_path = f"{current_plugin_path}:{gz_ros2_control_plugin_path}"
    else:
        new_plugin_path = gz_ros2_control_plugin_path
    
    # Environment variable'ı ayarla
    os.environ["GZ_SIM_SYSTEM_PLUGIN_PATH"] = new_plugin_path
    
    declared_arguments = []
    # UR specific arguments
    declared_arguments.append(
        DeclareLaunchArgument(
            "ur_type",
            description="Type/series of used UR robot.",
            choices=[
                "ur3",
                "ur3e",
                "ur5",
                "ur5e",
                "ur7e",
                "ur10",
                "ur12e",
                "ur10e",
                "ur16e",
                "ur20",
                "ur30",
            ],
            default_value="ur5e",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "safety_limits",
            default_value="true",
            description="Enables the safety limits controller if true.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "safety_pos_margin",
            default_value="0.15",
            description="The margin to lower and upper limits in the safety controller.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "safety_k_position",
            default_value="20",
            description="k-position factor in the safety controller.",
        )
    )
    # General arguments
    declared_arguments.append(
        DeclareLaunchArgument(
            "runtime_config_package",
            default_value="ur_simulation_gazebo",
            description='Package with the controller\'s configuration in "config" folder. \
        Usually the argument is not set, it enables use of a custom setup.',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "controllers_file",
            default_value="ur_controllers.yaml",
            description="YAML file with the controllers configuration.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "initial_positions_file",
            default_value=PathJoinSubstitution(
                [
                    FindPackageShare("ur_description"),
                    "config",
                    "initial_positions.yaml",
                ]
            ),
            description="YAML file (absolute path) with the robot's initial joint positions.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "description_package",
            default_value="ur_description",
            description="Description package with robot URDF/XACRO files. Usually the argument \
        is not set, it enables use of a custom description.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "description_file",
            default_value="ur.urdf.xacro",
            description="URDF/XACRO description file with the robot.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "prefix",
            default_value='""',
            description="Prefix of the joint names, useful for \
        multi-robot setup. If changed than also joint names in the controllers' configuration \
        have to be updated.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "start_joint_controller",
            default_value="true",
            description="Enable headless mode for robot control",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "initial_joint_controller",
            default_value="joint_trajectory_controller",
            description="Robot controller to start.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument("launch_rviz", default_value="true", description="Launch RViz?")
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "gazebo_gui", default_value="true", description="Start gazebo with GUI?"
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "gz_args", default_value="", description="Arguments for Gazebo Sim"
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
