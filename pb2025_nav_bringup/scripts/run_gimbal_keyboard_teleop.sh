#!/bin/bash
# Run gimbal keyboard teleop in current terminal (has TTY for keyboard).
# Usage: ./run_gimbal_keyboard_teleop.sh
# Or:   bash run_gimbal_keyboard_teleop.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# From lib/pkg or scripts/ -> workspace install dir
INSTALL_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
source "$INSTALL_DIR/setup.bash"
exec ros2 run pb2025_nav_bringup gimbal_keyboard_teleop.py \
  --ros-args -r __ns:=/red_standard_robot1 -p gimbal_yaw_speed:=0.2 -p cmd_spin_topic:=cmd_spin
