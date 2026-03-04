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
Gimbal yaw keyboard teleop. Publishes Float32 to cmd_spin topic.
Left/Right arrow keys control gimbal yaw (chassis spin) speed.
Requires a real TTY - run via gimbal_keyboard_teleop_launch.py which opens a new terminal.
"""

import sys

if sys.platform == "win32":
    import msvcrt
else:
    import select
    import termios
    import tty

import rclpy
from example_interfaces.msg import Float32


msg = """
Gimbal Yaw Keyboard Teleop
---------------------------
  Left arrow   : spin left (negative)
  Right arrow  : spin right (positive)
  Space/Down   : stop (zero)
  q            : quit
---------------------------
"""

# ANSI escape codes for arrow keys (Linux/Unix)
KEY_LEFT = "\x1b[D"
KEY_RIGHT = "\x1b[C"
KEY_DOWN = "\x1b[B"
KEY_UP = "\x1b[A"


def get_key(settings, timeout=0.05):
    """Read a single key with optional timeout (non-blocking)."""
    if sys.platform == "win32":
        if msvcrt.kbhit():
            key = msvcrt.getwch()
            if key == "\xe0":  # Arrow key prefix on Windows
                key += msvcrt.getwch()
            return key
        return None
    else:
        if select.select([sys.stdin], [], [], timeout)[0]:
            # Already in raw mode from main()
            key = sys.stdin.read(1)
            if key == "\x1b":  # Escape sequence (arrow keys)
                key += sys.stdin.read(2)
            return key
        return None


def main():
    # Check for TTY when not in a real terminal (e.g. launched from IDE)
    if not sys.stdin.isatty() and sys.platform != "win32":
        print(
            "Warning: stdin is not a TTY. Keyboard input may not work.\n"
            "Run via: ros2 launch pb2025_nav_bringup gimbal_keyboard_teleop_launch.py\n"
            "That opens a new terminal with proper TTY.",
            file=sys.stderr,
        )

    rclpy.init()
    node = rclpy.create_node("gimbal_keyboard_teleop")

    # Parameters
    node.declare_parameter("gimbal_yaw_speed", 0.2)
    node.declare_parameter("cmd_spin_topic", "cmd_spin")
    speed = node.get_parameter("gimbal_yaw_speed").value
    topic = node.get_parameter("cmd_spin_topic").value

    pub = node.create_publisher(Float32, topic, 10)
    spin_msg = Float32()

    if sys.platform != "win32":
        settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
    else:
        settings = None

    print(msg)
    print(f"Speed: {speed}  Topic: {topic}")
    print("Waiting for key input...")

    current_spin = 0.0

    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.01)
            key = get_key(settings)

            if key == "q" or key == "Q" or key == "\x03":  # Ctrl-C
                break
            elif key == KEY_LEFT:
                current_spin = -speed
            elif key == KEY_RIGHT:
                current_spin = speed
            elif key in (" ", KEY_DOWN):
                current_spin = 0.0

            spin_msg.data = float(current_spin)
            pub.publish(spin_msg)

    finally:
        # Stop on exit
        spin_msg.data = 0.0
        pub.publish(spin_msg)
        if sys.platform != "win32" and settings is not None:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
            except Exception:
                pass
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
