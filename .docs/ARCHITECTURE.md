<!-- LOC cap: 198 (source: 990, ratio: 0.20, updated: 2026-03-30) -->
# ARCHITECTURE

## System Overview

ASPECT is a ROS 2 Jazzy colcon monorepo. All development runs inside Docker; the host
machine only needs Docker Engine and `rocker`.

```
[Gazebo Harmonic sim]  ──gz_bridge──►  /odometry/raw  ──► [robot_localization EKF]
                                                                    │
                                                          /odometry/filtered
                                                                    │
                                                                    ▼
[aspect_navigation]  ──► /cmd_vel ──gz_bridge──► Gazebo /model/aspect_rover/cmd_vel
[aspect_control]     ──► /cmd_vel

[aspect_bringup]  launches gz sim -s (server-only) with aspect_gazebo world
[aspect_description]  provides URDF to robot_state_publisher
```

## Packages

| Package | Type | Role |
|---|---|---|
| `aspect_bringup` | ament_python | Launch files; entry point for simulation |
| `aspect_description` | ament_cmake | URDF/xacro model; 4-wheel diff-drive + IMU + camera |
| `aspect_control` | ament_python | Teleoperation node; publishes `/cmd_vel` |
| `aspect_navigation` | ament_python | Proportional waypoint nav; `/odometry/filtered` → `/cmd_vel` |
| `aspect_gazebo` | ament_cmake | SDF world (SDF 1.9); lunar south pole heightmap DEM |
| `aspect_msgs` | ament_cmake | Custom service: `GotoWaypoint.srv` |

## Data Flow

```
Simulation startup:
  aspect_bringup → gz sim -s lunar_south_pole.world  (server-only, starts paused)
                 → unpause: gz service /world/lunar_south_pole/control pause:false
                 → robot_state_publisher (URDF from aspect_description)
                 → ros_gz_bridge (cmd_vel, odometry, joint_states, imu, clock)
                 → robot_localization EKF (odometry/raw + imu → odometry/filtered)

Teleoperation:
  keyboard (termios) → aspect_control/teleop_node → /cmd_vel
    → ros_gz_bridge → Gazebo /model/aspect_rover/cmd_vel → DiffDrive plugin

Autonomous navigation:
  /goto_waypoint service → aspect_navigation/simple_waypoint_nav
    → subscribes /odometry/filtered → proportional P-controller
    → /cmd_vel

Nav2 stack (nav2.launch.py — T-010, Phase 0 partial):
  lifecycle_manager_navigation
    → planner_server (NavFn/Dijkstra global planner)
      → global_costmap (static layer, /map frame)
    → bt_navigator   (NavigateToPose / NavigateThroughPoses actions)
      → local_costmap (rolling window, odom frame)
      → /plan         (nav_msgs/Path)
```

## Key Interfaces

| Topic / Service | Type | Direction | Notes |
|---|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | control/nav → sim | ROS side; bridged to `/model/aspect_rover/cmd_vel` in Gz |
| `/odometry/raw` | `nav_msgs/Odometry` | sim → EKF | Bridged from `/model/aspect_rover/odometry` |
| `/odometry/filtered` | `nav_msgs/Odometry` | EKF → nav | Published by `robot_localization`; needs clock (~12 s warmup) |
| `/model/aspect_rover/imu` | `sensor_msgs/Imu` | sim → EKF | Bridged from Gazebo IMU sensor |
| `/clock` | `rosgraph_msgs/Clock` | sim → all nodes | Lazy-bridged; subscribe first to trigger |
| `/joint_states` | `sensor_msgs/JointState` | sim → RSP | Bridged from `/model/aspect_rover/joint_states` |
| `/goto_waypoint` | `aspect_msgs/GotoWaypoint` | client → nav node | Service; sets (x, y) goal in odom frame |
| `/navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | client → nav2 | Action server provided by `bt_navigator` |
| `/navigate_through_poses` | `nav2_msgs/action/NavigateThroughPoses` | client → nav2 | Action server provided by `bt_navigator` |
| `/plan` | `nav_msgs/Path` | nav2 → client | Global path published by `planner_server` |
| `/global_costmap/costmap` | `nav_msgs/OccupancyGrid` | nav2 → client | Published by global costmap node |
| `/local_costmap/costmap` | `nav_msgs/OccupancyGrid` | nav2 → client | Published by local costmap node |

## Infrastructure

- **Container:** `osrf/ros:jazzy-desktop` + `gz-harmonic` + `ros-jazzy-ros-gz` +
  `ros-jazzy-robot-localization` + `ros-jazzy-topic-tools` +
  `ros-jazzy-nav2-costmap-2d` + `ros-jazzy-nav2-planner` + `ros-jazzy-nav2-navfn-planner` +
  `ros-jazzy-nav2-bt-navigator` + `ros-jazzy-nav2-lifecycle-manager`
- **Python tooling:** `uv` — never `pip` or `python` directly
- **Resource path:** `GZ_SIM_RESOURCE_PATH=/workspace/install/aspect_gazebo/share/aspect_gazebo`
  set in Dockerfile; world SDF uses `model://` URIs resolved against it
- **Linting:** `ament_flake8` (PEP 8, max 99 chars) + `ament_pep257` + `ament_copyright`
  (enabled in all packages; T-003/T-004 complete)
- **Physics:** dartsim cannot use heightmap collision geometry; flat `ground_plane`
  model added to world SDF to provide collision surface

## Known Stubs / Limitations

- `aspect_description` URDF: box geometry only; real meshes not yet modelled
- EKF `/odometry/filtered`: requires `/clock` to start (~12 s after unpause); do not
  use for navigation until warmup completes
- Heightmap collision: dartsim silently skips heightmap collision; rover drives on
  invisible flat plane at z=0 — visual-only heightmap until physics engine supports it
- Gazebo GUI: not available in headless container; use `rocker --x11` on host for GUI
