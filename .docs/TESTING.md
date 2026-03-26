<!-- LOC cap: 60 (source: 300, ratio: 0.20, updated: 2026-03-26) -->
# TESTING

All testing runs **inside the Docker container**. See `AGENTS.md` for container entry commands.

---

## Prerequisites

> Enter the container, build, and source before any test step below.

```bash
colcon build --symlink-install && source install/setup.bash
```

Pass: all 6 packages (`aspect_msgs`, `aspect_bringup`, `aspect_control`,
`aspect_description`, `aspect_gazebo`, `aspect_navigation`) finish with no `ERROR`.

---

## T-L1 — Linter

```bash
colcon test --packages-select aspect_control aspect_navigation
colcon test-result --verbose
```

Pass: flake8, pep257, copyright all green.

---

## T-S1 — Topic smoke test

```bash
ros2 launch aspect_bringup launch_lunar_south_pole.py
# in a second shell:
ros2 topic list
```

Pass: all topics present.

| Topic | Type |
|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` |
| `/odometry/raw` | `nav_msgs/Odometry` |
| `/odometry/filtered` | `nav_msgs/Odometry` |
| `/model/aspect_rover/imu` | `sensor_msgs/Imu` |
| `/clock` | `rosgraph_msgs/Clock` |
| `/tf` | `tf2_msgs/TFMessage` |

---

## T-D1 — Manual drive

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.2}, angular: {z: 0.0}}"
ros2 topic echo /odometry/filtered --once
```

Pass: `pose.pose.position.x` non-zero after publish.

---

## T-D2 — Waypoint service

```bash
ros2 service call /goto_waypoint aspect_msgs/srv/GotoWaypoint "{x: 2.0, y: 0.0}"
ros2 topic echo /cmd_vel
```

Pass: service returns `success: true`; `/cmd_vel` publishes non-zero until goal reached, then zeros.

---

## T-D3 — Keyboard teleop

```bash
ros2 run aspect_control teleop_node   # requires -it TTY
```

Pass: `w` → forward velocity on `/cmd_vel`; `space` → zeros; `q` → clean exit + zero stop.

---

## Not yet testable

| Item | Blocker |
|---|---|
| Gazebo GUI / meshes | T-005 (no real URDF meshes yet) |
| nav2 costmap | T-010 not implemented |
| 30-min stability | T-107, Phase 1 |
