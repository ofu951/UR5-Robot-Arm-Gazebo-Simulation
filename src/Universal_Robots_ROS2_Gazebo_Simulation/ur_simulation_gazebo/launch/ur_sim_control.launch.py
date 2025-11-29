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
    ExecuteProcess,
    IncludeLaunchDescription,
    OpaqueFunction,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
import os
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def launch_setup(context, *args, **kwargs):
    # Initialize Arguments
    ur_type = LaunchConfiguration("ur_type")
    safety_limits = LaunchConfiguration("safety_limits")
    safety_pos_margin = LaunchConfiguration("safety_pos_margin")
    safety_k_position = LaunchConfiguration("safety_k_position")
    description_package = LaunchConfiguration("description_package")
    description_file = LaunchConfiguration("description_file")
    prefix = LaunchConfiguration("prefix")
    launch_rviz = LaunchConfiguration("launch_rviz")
    gz_version = LaunchConfiguration("gz_version")

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare(description_package), "rviz", "view_robot.rviz"]
    )

    # Basit robot description - ros2_control olmadan (my_rrr_robot gibi)
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
            "name:=ur",
            " ",
            "ur_type:=",
            ur_type,
            " ",
            "prefix:=",
            prefix,
        ]
    )
    
    robot_description = ParameterValue(
        robot_description_content,
        value_type=str
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description, "use_sim_time": True}],
    )

    # Joint state publisher GUI (my_rrr_robot gibi)
    joint_state_publisher_gui = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        output="screen",
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config_file],
        condition=IfCondition(launch_rviz),
    )

    # Gazebo launch (my_rrr_robot gibi)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("ros_gz_sim"), "/launch", "/gz_sim.launch.py"]
        ),
        launch_arguments={
            "gz_args": "",
            "gz_version": gz_version,
        }.items(),
    )

    # Robot spawn - yere yerleştir (masa yok)
    spawn_robot = TimerAction(
        period=3.0,
        actions=[
            Node(
                package="ros_gz_sim",
                executable="create",
                name="spawn_ur5",
                arguments=[
                    "-name", "ur",
                    "-topic", "robot_description",
                    "-x", "0.0",
                    "-y", "0.0",
                    "-z", "0.0",  # Yere yerleştir (masa yok)
                ],
                output="screen",
            )
        ],
    )

    # ROS <-> Gazebo joint bridge (my_rrr_robot gibi - UR5'in 6 eklemi için)
    joint_bridge = Node(
        package="ros_gz_bridge",
        executable="bridge_node",
        name="ur5_joint_bridge",
        parameters=[{
            "bridges": {
                "shoulder_pan_bridge": {
                    "ros_topic_name": "/ur/shoulder_pan_joint/command",
                    "ros_type_name": "std_msgs/msg/Float64",
                    "gz_topic_name": "/model/ur/joint/shoulder_pan_joint/0/cmd_pos",
                    "gz_type_name": "gz.msgs.Double",
                    "direction": "ROS_TO_GZ",
                },
                "shoulder_lift_bridge": {
                    "ros_topic_name": "/ur/shoulder_lift_joint/command",
                    "ros_type_name": "std_msgs/msg/Float64",
                    "gz_topic_name": "/model/ur/joint/shoulder_lift_joint/0/cmd_pos",
                    "gz_type_name": "gz.msgs.Double",
                    "direction": "ROS_TO_GZ",
                },
                "elbow_bridge": {
                    "ros_topic_name": "/ur/elbow_joint/command",
                    "ros_type_name": "std_msgs/msg/Float64",
                    "gz_topic_name": "/model/ur/joint/elbow_joint/0/cmd_pos",
                    "gz_type_name": "gz.msgs.Double",
                    "direction": "ROS_TO_GZ",
                },
                "wrist_1_bridge": {
                    "ros_topic_name": "/ur/wrist_1_joint/command",
                    "ros_type_name": "std_msgs/msg/Float64",
                    "gz_topic_name": "/model/ur/joint/wrist_1_joint/0/cmd_pos",
                    "gz_type_name": "gz.msgs.Double",
                    "direction": "ROS_TO_GZ",
                },
                "wrist_2_bridge": {
                    "ros_topic_name": "/ur/wrist_2_joint/command",
                    "ros_type_name": "std_msgs/msg/Float64",
                    "gz_topic_name": "/model/ur/joint/wrist_2_joint/0/cmd_pos",
                    "gz_type_name": "gz.msgs.Double",
                    "direction": "ROS_TO_GZ",
                },
                "wrist_3_bridge": {
                    "ros_topic_name": "/ur/wrist_3_joint/command",
                    "ros_type_name": "std_msgs/msg/Float64",
                    "gz_topic_name": "/model/ur/joint/wrist_3_joint/0/cmd_pos",
                    "gz_type_name": "gz.msgs.Double",
                    "direction": "ROS_TO_GZ",
                },
            },
            "bridge_names": [
                "shoulder_pan_bridge",
                "shoulder_lift_bridge",
                "elbow_bridge",
                "wrist_1_bridge",
                "wrist_2_bridge",
                "wrist_3_bridge",
            ],
        }],
        output="screen",
    )

    # Initial position setter - robot spawn olduktan sonra home position'a getir
    # Script path'ini bul
    script_path = os.path.expanduser("~/UR5-Robot-Arm-Gazebo-Simulation/set_initial_positions.py")
    
    initial_position_setter = TimerAction(
        period=5.0,  # Robot spawn olduktan 5 saniye sonra
        actions=[
            ExecuteProcess(
                cmd=["python3", script_path],
                name="ur5_initial_position_setter",
                output="screen",
            )
        ],
    )
    
    # Joint Controller GUI - trackbar ile kontrol
    gui_script_path = os.path.expanduser("~/UR5-Robot-Arm-Gazebo-Simulation/ur5_joint_controller_gui.py")
    
    joint_controller_gui = TimerAction(
        period=2.0,  # Gazebo açıldıktan 2 saniye sonra GUI'yi aç
        actions=[
            ExecuteProcess(
                cmd=["python3", gui_script_path],
                name="ur5_joint_controller_gui",
                output="screen",
            )
        ],
    )

    nodes_to_start = [
        robot_state_publisher_node,
        joint_state_publisher_gui,
        gazebo,
        spawn_robot,  # Masa kaldırıldı
        joint_bridge,
        initial_position_setter,  # Home position'a getir
        joint_controller_gui,  # Trackbar GUI
        rviz_node,
    ]

    return nodes_to_start


def generate_launch_description():
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
        DeclareLaunchArgument("launch_rviz", default_value="true", description="Launch RViz?")
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "gz_version",
            default_value="8",
            description="Gazebo Sim major version to use when launching gz_sim",
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
