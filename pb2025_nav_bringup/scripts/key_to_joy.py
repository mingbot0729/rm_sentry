#!/usr/bin/env python3
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
Keyboard-to-Joy: publishes sensor_msgs/Joy from arrow keys for pb_teleop_twist_joy.
Maps: Left/Right -> axis 3 (gimbal yaw) only. Always enabled, no enable button.
Requires TTY - run in a terminal.
"""

import sys

if sys.platform == "win32":
    import msvcrt
else:
    import select
    import termios
    import tty

import rclpy
from sensor_msgs.msg import Joy


msg = """
Keyboard to Joy (Gimbal yaw only)
---------------------------------
  Left/Right  : gimbal yaw (axis 3)
  q           : quit
---------------------------------
"""

KEY_LEFT = "\x1b[D"
KEY_RIGHT = "\x1b[C"


def get_key(settings, timeout=0.05):
    if sys.platform == "win32":
        if msvcrt.kbhit():
            key = msvcrt.getwch()
            if key == "\xe0":
                key += msvcrt.getwch()
            return key
        return None
    else:
        if select.select([sys.stdin], [], [], timeout)[0]:
            key = sys.stdin.read(1)
            if key == "\x1b":
                key += sys.stdin.read(2)
            return key
        return None


def main():
    if not sys.stdin.isatty() and sys.platform != "win32":
        print(
            "Warning: stdin is not a TTY. Run in a terminal.\n"
            "ros2 run pb2025_nav_bringup key_to_joy.py",
            file=sys.stderr,
        )

    rclpy.init()
    node = rclpy.create_node("key_to_joy")

    pub = node.create_publisher(Joy, "joy", 10)

    if sys.platform != "win32":
        settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
    else:
        settings = None

    print(msg)

    # Joy: axes[3]=yaw (-1 left, +1 right) only
    joy_msg = Joy()
    joy_msg.axes = [0.0] * 8
    joy_msg.buttons = [0] * 8

    IDLE_TIMEOUT = 0.15  # Zero yaw after this many seconds with no key
    last_key_time = node.get_clock().now().nanoseconds / 1e9

    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.01)
            now = node.get_clock().now().nanoseconds / 1e9
            key = get_key(settings)

            if key == "q" or key == "Q" or key == "\x03":
                break
            elif key == KEY_LEFT:
                joy_msg.axes[3] = -1.0
                last_key_time = now
            elif key == KEY_RIGHT:
                joy_msg.axes[3] = 1.0
                last_key_time = now
            elif key is not None:
                joy_msg.axes[3] = 0.0
                last_key_time = now
            elif now - last_key_time > IDLE_TIMEOUT:
                joy_msg.axes[3] = 0.0

            joy_msg.header.stamp = node.get_clock().now().to_msg()
            joy_msg.header.frame_id = "keyboard"
            pub.publish(joy_msg)

    finally:
        joy_msg.axes[3] = 0.0
        pub.publish(joy_msg)
        if sys.platform != "win32" and settings is not None:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
            except Exception:
                pass
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
