<!-- LOC cap: 156 (source: 780, ratio: 0.20, updated: 2026-03-26) -->
# ARCHITECTURE

## System Overview

ASPECT is a ROS 2 Jazzy colcon monorepo. All development runs inside Docker; the host
machine only needs Docker Engine and `rocker`.

```
[Gazebo Harmonic sim]
        │ /odometry/filtered (nav_msgs/Odometry)
        ▼
[aspect_navigation]  ──► /cmd_vel (geometry_msgs/Twist) ──► [Gazebo / hardware]
[aspect_control]     ──► /cmd_vel

[aspect_bringup]  launches gz sim with aspect_gazebo world
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

## Data Flow

```
Simulation startup:
  aspect_bringup → gz sim lunar_south_pole.world
                 → robot_state_publisher (URDF from aspect_description)

Teleoperation:
  keyboard/joy → aspect_control/teleop_node → /cmd_vel → diff-drive plugin

Autonomous navigation:
  EKF odometry → aspect_navigation/simple_waypoint_nav
              → proportional P-controller (heading + distance)
              → /cmd_vel
```

## Key Interfaces

| Topic | Type | Direction |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | written by control & nav; read by sim/hardware |
| `/odometry/filtered` | `nav_msgs/Odometry` | written by EKF (`robot_localization`) |
| `/joint_states` | `sensor_msgs/JointState` | published by `joint_state_publisher_gui` in viz mode |

## Infrastructure

- **Container:** `osrf/ros:jazzy-desktop` + `gz-harmonic` + `ros-jazzy-ros-gz`
- **Python tooling:** `uv` — never `pip` or `python` directly
- **Resource path:** `GZ_SIM_RESOURCE_PATH=/workspace/install/aspect_gazebo/share/aspect_gazebo`
  set in Dockerfile; world SDF uses `model://` URIs resolved against it
- **Linting:** `ament_flake8` (PEP 8, max 99 chars) + `ament_pep257`; copyright check
  currently skipped (headers pending — see [BUGS.md](bugs/BUGS.md))

## Known Stubs

- `aspect_description` URDF: box geometry only; real meshes not yet modelled
- `aspect_control/teleop_node.py`: publisher exists; keyboard capture not implemented
- `aspect_navigation/simple_waypoint_nav.py`: P-controller functional; `/goto_waypoint`
  service not yet exposed — see [BUGS.md](bugs/BUGS.md) and [ROADMAP.md](features/open/ROADMAP.md)
