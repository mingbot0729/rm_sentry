# Copyright 2025 Lihan Chen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, GroupAction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, PushRosNamespace, SetRemap
from launch_ros.descriptions import ParameterFile
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    # Get the package directory and run script path
    bringup_dir = get_package_share_directory("pb2025_nav_bringup")
    pkg_install_dir = os.path.dirname(os.path.dirname(bringup_dir))
    run_key_to_joy_script = os.path.join(
        pkg_install_dir, "lib", "pb2025_nav_bringup", "run_key_to_joy.sh"
    )

    # Create the launch configuration variables
    namespace = LaunchConfiguration("namespace")
    use_sim_time = LaunchConfiguration("use_sim_time")
    use_keyboard = LaunchConfiguration("use_keyboard")
    joy_vel = LaunchConfiguration("joy_vel")
    joy_dev = LaunchConfiguration("joy_dev")
    joy_config_file = LaunchConfiguration("joy_config_file")

    # Create our own temporary YAML files that include substitutions
    # When use_keyboard: require_enable_button=false (always enabled, no Space needed)
    param_substitutions = {
        "use_sim_time": use_sim_time,
        "pb_teleop_twist_joy_node.ros__parameters.require_enable_button": PythonExpression(
            ["'false' if '", use_keyboard, "' == 'true' else 'true'"]
        ),
    }

    configured_params = ParameterFile(
        RewrittenYaml(
            source_file=joy_config_file,
            root_key=namespace,
            param_rewrites=param_substitutions,
            convert_types=True,
        ),
        allow_substs=True,
    )

    # Declare the launch arguments
    declare_namespace_cmd = DeclareLaunchArgument(
        "namespace",
        default_value="",
        description="Top-level namespace",
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description="Use simulation (Gazebo) clock if true",
    )

    declare_joy_vel_cmd = DeclareLaunchArgument(
        "joy_vel",
        default_value="cmd_vel",
        description="The topic to publish velocity commands to",
    )

    declare_joy_config_file_cmd = DeclareLaunchArgument(
        "joy_config_file",
        default_value=os.path.join(
            bringup_dir, "config", "simulation", "nav2_params.yaml"
        ),
        description="The joystick configuration file path",
    )

    declare_joy_dev_cmd = DeclareLaunchArgument(
        "joy_dev", default_value="0", description="The joystick device ID"
    )

    declare_use_keyboard_cmd = DeclareLaunchArgument(
        "use_keyboard",
        default_value="false",
        description="Use keyboard (arrow keys) instead of physical joystick for gimbal control",
    )

    # When use_keyboard: run key_to_joy in a new terminal (needs TTY). Publishes to /joy.
    # Use run_key_to_joy.sh which sources itself (spawned terminal doesn't inherit env).
    run_key_to_joy_cmd = ExecuteProcess(
        cmd=["x-terminal-emulator", "-e", run_key_to_joy_script],
        output="screen",
        condition=IfCondition(use_keyboard),
        additional_env={"KEYBOARD_NS": namespace},
    )

    bringup_cmd_group = GroupAction(
        [
            PushRosNamespace(namespace=namespace),
            SetRemap("/tf", "tf"),
            SetRemap("/tf_static", "tf_static"),
            Node(
                package="joy",
                executable="joy_node",
                name="joy_node",
                output="screen",
                parameters=[
                    {
                        "device_id": joy_dev,
                        "deadzone": 0.3,
                        "autorepeat_rate": 20.0,
                    }
                ],
                condition=UnlessCondition(use_keyboard),
            ),
            Node(
                package="pb_teleop_twist_joy",
                executable="pb_teleop_twist_joy_node",
                name="pb_teleop_twist_joy_node",
                output="screen",
                parameters=[configured_params],
                remappings=[
                    ("/cmd_vel", joy_vel),
                    ("/tf", "tf"),
                    ("/tf_static", "tf_static"),
                ],
            ),
        ]
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(declare_namespace_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_use_keyboard_cmd)
    ld.add_action(declare_joy_vel_cmd)
    ld.add_action(declare_joy_config_file_cmd)
    ld.add_action(declare_joy_dev_cmd)

    # Add the actions to launch the nodes
    ld.add_action(run_key_to_joy_cmd)
    ld.add_action(bringup_cmd_group)

    return ld
