cmake_minimum_required(VERSION 3.8)
project(pb2025_nav_bringup)

find_package(ament_cmake_auto REQUIRED)

if(BUILD_TESTING)
find_package(ament_lint_auto REQUIRED)
  list(APPEND AMENT_LINT_AUTO_EXCLUDE
    ament_cmake_uncrustify
    ament_cmake_cpplint
    ament_cmake_flake8
  )
  ament_lint_auto_find_test_dependencies()
endif()

ament_auto_package(
  INSTALL_TO_SHARE
  launch
  map
  pcd
  config
  behavior_trees
  rviz
)

# Install gimbal keyboard teleop script and run helper
install(PROGRAMS
  scripts/gimbal_keyboard_teleop.py
  scripts/key_to_joy.py
  scripts/run_gimbal_keyboard_teleop.sh
  scripts/run_key_to_joy.sh
  DESTINATION lib/${PROJECT_NAME}
)
