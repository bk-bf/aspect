<!-- LOC cap: 156 (source: 780, ratio: 0.20, updated: 2026-03-26) -->
# BUGS

Known defects and technical debt. Use `B-NNN` IDs. Mark resolved items with date.

---

## Open

| ID | Severity | Description | Location |
|---|---|---|---|
| B-001 | Low | Apache 2.0 copyright headers absent from all files except `teleop_node.py` and `simple_waypoint_nav.py` | All packages |
| B-002 | Low | `ament_copyright` linter check disabled (`ament_cmake_copyright_FOUND TRUE`) pending B-001 | All `CMakeLists.txt` / test suites |
| B-003 | Low | `aspect_description/resource/` directory is empty — harmless for `ament_cmake` but leftover from scaffold | `aspect_description/resource/` |
| B-004 | Medium | `teleop_node.py`: keyboard capture not implemented; node starts but accepts no input | `aspect_control/teleop_node.py:29` |
| B-005 | Medium | `simple_waypoint_nav.py`: `/goto_waypoint` service not exposed; goals can only be set programmatically via `set_goal()` | `aspect_navigation/simple_waypoint_nav.py:28` |
---

## Resolved

| ID | Date | Description |
|---|---|---|
| B-000 | 2026-03-26 | Hardcoded absolute paths in launch file and world SDF — replaced with `get_package_share_directory` and `model://` URIs |
| B-006 | 2026-03-26 | `ros_gz_bridge` added in `launch_lunar_south_pole.py`; bridges `/cmd_vel`, `/odometry/raw`, `/joint_states`, `/imu`, `/clock` |
| B-007 | 2026-03-26 | Rover URDF spawned at launch via `ros_gz_sim create` node (delayed 3 s); `robot_state_publisher` added |
| B-008 | 2026-03-26 | Diff-drive + joint-state-publisher + IMU sensor plugins added to `aspect_rover.urdf.xacro` as Gazebo extensions |
