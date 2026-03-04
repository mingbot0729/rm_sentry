#!/bin/bash
# Run key_to_joy in current terminal (has TTY for keyboard).
# Left/Right arrow keys → gimbal yaw only (no joystick needed).
# Publishes sensor_msgs/Joy to /joy for pb_teleop_twist_joy.
# Preferred: ros2 launch pb2025_nav_bringup joy_teleop_launch.py use_keyboard:=true
# Or run this script manually: ./run_key_to_joy.sh
# Or:   KEYBOARD_NS=red_standard_robot1 ./run_key_to_joy.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
source "$INSTALL_DIR/setup.bash"

ns="${KEYBOARD_NS:-red_standard_robot1}"
if [ -n "$ns" ]; then
  ros2 run pb2025_nav_bringup key_to_joy.py --ros-args -r __ns:="/$ns"
else
  ros2 run pb2025_nav_bringup key_to_joy.py
fi
echo ""; echo "Press Enter to close..."; read
