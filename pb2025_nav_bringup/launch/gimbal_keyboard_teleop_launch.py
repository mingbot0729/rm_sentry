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
# WITHOUT WARRANTIES OR CONDITIONS FOR A PARTICULAR PURPOSE.  See the
# License for the specific language governing permissions and
# limitations under the License.

"""
Launch gimbal keyboard teleop in a new terminal (x-terminal-emulator) for TTY/keyboard input.
Left/Right arrows control gimbal yaw via cmd_spin topic.
Env is inherited from the launch process (source install/setup.bash before ros2 launch).
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    declare_namespace = DeclareLaunchArgument(
        "namespace",
        default_value="red_standard_robot1",
        description="Robot namespace",
    )

    declare_gimbal_yaw_speed = DeclareLaunchArgument(
        "gimbal_yaw_speed",
        default_value="0.2",
        description="Gimbal yaw speed (rad/s) when holding Left/Right arrow",
    )

    declare_cmd_spin_topic = DeclareLaunchArgument(
        "cmd_spin_topic",
        default_value="cmd_spin",
        description="Topic to publish spin commands (Float32)",
    )

    # Open new terminal. Env inherited from launch (user must source install/setup.bash before ros2 launch).
    bash_cmd = (
        "ros2 run pb2025_nav_bringup gimbal_keyboard_teleop.py "
        "--ros-args "
        "-r __ns:=/red_standard_robot1 "
        "-p gimbal_yaw_speed:=0.2 "
        "-p cmd_spin_topic:=cmd_spin; "
        "echo ''; echo 'Press Enter to close...'; read"
    )

    run_gimbal_teleop = ExecuteProcess(
        cmd=["x-terminal-emulator", "-e", "bash", "-c", bash_cmd],
        output="screen",
    )

    return LaunchDescription([
        declare_namespace,
        declare_gimbal_yaw_speed,
        declare_cmd_spin_topic,
        run_gimbal_teleop,
    ])
