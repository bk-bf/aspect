# AGENTS.md — ASPECT Rover Codebase Guide

**Project:** ASPECT (Autonomous Surface Precision Excavation for Celestial Terrain)  
**Stack:** ROS 2 Jazzy Jalisco · Gazebo Harmonic · Python · C++ · Docker · uv

---

## Project Overview

ASPECT is a ROS 2 robotics simulation and physical prototype of a lunar mining rover
for in-situ resource utilization (ISRU). The workspace is a colcon monorepo containing
multiple ament packages under `src/`.

Planning and architecture documents live in `.docs/` (Obsidian vault, not code).  
Docker infrastructure lives in `.docker/`.

> **Parent project docs:** The autoresearcher deployment that orchestrates this project maintains its own documentation at `../.docs/` (one level up, relative to `aspect/`). Key files:
> - `../.docs/ARCHITECTURE.md` — deployment topology, data flow, package management
> - `../.docs/PHILOSOPHY.md` — compute separation, overnight autonomy, provider strategy
> - `../.docs/DECISIONS.md` — deployment decisions (D-001 through D-005)
> - `../.docs/features/open/ROADMAP.md` — open tasks (T-001 through T-008)

---

## Repository Layout

```
aspect/
├── .docker/
│   ├── Dockerfile          # ROS 2 Jazzy + Gazebo Harmonic + uv
│   ├── docker-compose.yml  # Container orchestration
│   └── entrypoint.sh       # Sources ROS 2 + workspace overlay
├── .docs/                  # Planning docs (ASPECT.md, roadmap, weekly tasks)
├── AGENTS.md               # This file
└── src/
    ├── aspect_bringup/     # ament_python — launch files
    ├── aspect_description/ # ament_cmake  — URDF/xacro rover models
    ├── aspect_control/     # ament_python — teleoperation node
    ├── aspect_navigation/  # ament_python — waypoint nav node
    └── aspect_gazebo/      # ament_cmake  — SDF worlds, DEM media
```

---

## Docker Workflow

All development runs inside the Docker container. Never install ROS 2 or Gazebo on the
host directly — use the container.

```bash
# Build the image (first time: ~10 min)
docker build -f .docker/Dockerfile -t aspect:jazzy .

# Enter container with GUI (Gazebo, RViz2) via rocker — recommended for development
rocker --x11 --nvidia --user --volume $(pwd):/workspace aspect:jazzy

# Alternative: headless via docker compose
docker compose -f .docker/docker-compose.yml up -d
docker compose -f .docker/docker-compose.yml exec aspect_dev bash
```

---

## Build Commands

Run inside the container (workspace root `/workspace`):

```bash
# Build entire workspace
colcon build

# Build a single package
colcon build --packages-select aspect_navigation

# Symlink install (faster iteration for Python packages)
colcon build --symlink-install --packages-select aspect_control

# Source the install overlay after building
source install/setup.bash
```

---

## Test Commands

Tests use `pytest` under the hood, driven by `colcon test`.

```bash
# Run all tests
colcon test && colcon test-result --verbose

# Run tests for one package
colcon test --packages-select aspect_navigation

# Run a single test file directly (use uv, not python or pytest directly)
uv run pytest src/aspect_navigation/test/test_flake8.py -v

# Run a single test by name
uv run pytest src/aspect_navigation/test/test_flake8.py::test_flake8 -v

# Verbose colcon output
colcon test --packages-select aspect_bringup --event-handlers console_direct+
```

---

## Lint Commands

Linting uses the ROS 2 ament linter suite. Use `uv tool run` for direct invocations —
never `python -m` or bare `flake8`.

```bash
# Run flake8 via uv (preferred for direct invocation)
uv tool run flake8 src/aspect_control/aspect_control/

# Run pep257 via uv
uv tool run pydocstyle src/aspect_navigation/aspect_navigation/

# Run via colcon (canonical — matches CI)
colcon test --packages-select aspect_bringup --pytest-args -m flake8
colcon test --packages-select aspect_bringup --pytest-args -m pep257
```

---

## Python Tool Runner: uv

**Always use `uv` instead of `python`, `python3`, or `pip`.**

```bash
# Run a script
uv run python3 my_script.py

# Run pytest
uv run pytest src/aspect_navigation/test/ -v

# Install/run a tool (flake8, pytest, pydocstyle, rocker, etc.)
uv tool install flake8
uv tool run flake8 src/

# Install project dependencies from pyproject.toml (if present)
uv sync
```

`colcon build` manages its own Python environment for ament packages — do not interfere
with it via uv. Use uv only for running tools and scripts outside of colcon's build
graph.

---

## Launch Commands

```bash
# Launch lunar south pole simulation (server-only, headless — see Gazebo Quirks below)
ros2 launch aspect_bringup launch_lunar_south_pole.py

# Launch with a custom world path
ros2 launch aspect_bringup launch_lunar_south_pole.py world:=/path/to/world.sdf

# View rover URDF in RViz2
ros2 launch aspect_description view_urdf.launch.py

# Teleoperation node (requires interactive TTY: docker run -it)
ros2 launch aspect_control teleop.launch.py

# Waypoint navigation node (separate from main launch)
ros2 launch aspect_navigation waypoint_nav.launch.py
```

### Gazebo Quirks — read before running the sim

**1. Server-only mode (`-s` flag)**

`gz sim` normally starts both the GUI and the physics server as a single process.
In a headless container (no GPU / no display), the Qt/OGRE GUI thread crashes — and
**takes the physics server down with it**. The launch file uses `-s` (server-only) to
skip the GUI entirely. Never remove `-s` when running in the container without rocker.

```bash
# What the launch file runs (do not change inside container):
gz sim -s -v 4 <world.sdf>

# To get the GUI interactively, use rocker on the host:
rocker --x11 --nvidia --user --volume $(pwd):/workspace aspect:jazzy
# then inside the rocker shell, remove -s from the launch file or override:
ros2 launch aspect_bringup launch_lunar_south_pole.py
```

**2. Server-only starts paused**

When running with `-s`, Gazebo starts with the simulation **paused** — it normally
waits for the GUI client to unpause it. After launch, you must unpause manually:

```bash
gz service -s /world/lunar_south_pole/control \
  --reqtype gz.msgs.WorldControl \
  --reptype gz.msgs.Boolean \
  --timeout 5000 \
  --req 'pause: false'
```

Expected reply: `data: true`. Without this, `/clock` will not publish and the EKF
node will log `Waiting for clock to start...` indefinitely. `/odometry/raw` will also
not publish (physics not stepping).

**3. `/clock` bridge is lazy**

`ros_gz_bridge` creates subscriptions lazily. `/clock` only starts flowing into ROS 2
once something subscribes to it on the ROS side. `ros2 topic echo /clock` before the
bridge has connected will time out with a `does not appear to be published yet` warning
even though Gazebo is publishing. Give it 2–3 seconds or subscribe from a node first.

**4. `cmd_vel` topic routing**

The diff-drive plugin inside Gazebo listens on Gazebo topic
`/model/aspect_rover/cmd_vel`. The bridge argument is:

```
/model/aspect_rover/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist
```

with a ROS-side remapping that exposes it as `/cmd_vel`. Publishing to `/cmd_vel` in
ROS 2 therefore reaches the plugin. The bridge log confirms this:

```
Passing message from ROS geometry_msgs/msg/Twist to Gazebo gz.msgs.Twist
```

If you see the log line but the rover does not move, check that the sim is unpaused
(Quirk 2) and that physics has not crashed (Quirk 5).

**5. dartsim / ODE physics crash on contact**

dartsim's ODE LCP solver can abort with:

```
ODE INTERNAL ERROR 1: assertion "d[i] != dReal(0.0)" failed in _dLDLTRemove()
```

This happens when:
- The rover is spawned too high and falls with large impact energy (old default: z=0.5 m)
- Inertia tensors are physically inconsistent (old values: `ixx=iyy=izz=0.0001` for all)
- The world has no collision geometry (dartsim cannot use heightmap collision)

**Current fixes (already applied):**
- Default spawn z = 0.05 m (just above wheel radius)
- Chassis inertia corrected to box formula: `ixx=0.000273, iyy=0.000482, izz=0.000542`
- Wheel inertia corrected to cylinder formula: `ixx=iyy=0.000003, izz=0.000005`
- Flat `ground_plane` added to `lunar_south_pole.world` (heightmap visual kept; only
  collision is missing from dartsim)

**6. LSP false positives in ROS 2 files**

The host environment does not have a ROS 2 install overlay, so editors/LSP servers
report import errors for `rclpy`, `geometry_msgs`, `launch`, `ament_*`, `xacro`, etc.
**These are false positives.** All ROS 2 imports resolve correctly inside the container.
Do not add `# type: ignore` or `# noqa` comments to suppress them — they will cause
pep257/flake8 failures inside the container.

```
# Expected false-positive LSP errors (host only — safe to ignore):
ERROR: Import "rclpy" could not be resolved
ERROR: Import "geometry_msgs.msg" could not be resolved
ERROR: Import "launch.actions" could not be resolved
ERROR: Import "xacro" could not be resolved
ERROR: "LaunchDescription" is unknown import symbol
```

---

## Code Style — Python

### Formatting
- **PEP 8** enforced by `ament_flake8`. Max line length: 99 characters.
- **PEP 257** docstrings enforced by `ament_pep257`.
- 4-space indentation; no tabs.

### Imports
- Standard library first, then third-party, then ROS 2 / local.
- One import per line; no wildcard imports (`from foo import *`).
- Example:
  ```python
  import math
  import os

  from geometry_msgs.msg import Twist
  from nav_msgs.msg import Odometry
  import rclpy
  from rclpy.node import Node
  ```

### Naming Conventions
- **Modules/files:** `snake_case.py`
- **Functions/methods:** `snake_case`
- **Classes:** `PascalCase`
- **Constants:** `UPPER_SNAKE_CASE`
- **ROS 2 topics/services:** `snake_case` with leading `/` (e.g., `/cmd_vel`, `/odometry/filtered`)
- **ROS 2 node names:** `snake_case` (e.g., `simple_waypoint_nav`)

### Type Annotations
- Add type annotations to all new Python nodes and utilities.
- Use `from __future__ import annotations` if needed for forward references.
- Use `list | None` syntax (Python 3.10+), not `Optional[list]`.

### Error Handling
- Launch files: no try/except — errors surface at runtime per ROS 2 convention.
- Node code: use `self.get_logger().error(...)`, never `print()`.
- Use `.warn(...)` for recoverable issues, `.info(...)` for status.

### ROS 2 Node Pattern
```python
"""One-line module docstring."""

import rclpy
from rclpy.node import Node


class MyNode(Node):
    """Node docstring."""

    def __init__(self) -> None:
        """Initialise node."""
        super().__init__('my_node')

def main(args: list | None = None) -> None:
    """Entry point."""
    rclpy.init(args=args)
    node = MyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

---

## Code Style — C++ (ament_cmake packages)

- C++17 standard.
- Compiler flags: `-Wall -Wextra -Wpedantic` in all CMake packages.
- Follow the ROS 2 C++ style guide: `snake_case` variables/functions, `PascalCase` classes,
  `ALL_CAPS` constants.
- Include guards: `#pragma once`.
- No raw owning pointers; prefer `std::shared_ptr` / `std::unique_ptr`.

---

## Code Style — URDF / xacro

- Use **xacro macros** for repeated elements (wheels, joints).
- Always specify `<inertial>` for every `<link>`.
- Parametric positioning with named params (e.g., `reflect_lr`, `reflect_fb`).
- File: `aspect_description/urdf/aspect_rover.urdf.xacro`

---

## Code Style — SDF / Gazebo Worlds

- SDF 1.9 (Gazebo Harmonic).
- **Never hardcode absolute paths.** Use `model://` URIs resolved via `GZ_SIM_RESOURCE_PATH`.
- The Dockerfile sets `GZ_SIM_RESOURCE_PATH` automatically.
- Outside Docker: `export GZ_SIM_RESOURCE_PATH=$(ros2 pkg prefix aspect_gazebo)/share/aspect_gazebo`

---

## Package Configuration

### Adding a new ament_python package
1. `package.xml` with `<build_type>ament_python</build_type>`.
2. Add `ament_flake8`, `ament_pep257`, `python3-pytest` as `<test_depend>`.
3. Copy `test/test_flake8.py`, `test/test_pep257.py`, `test/test_copyright.py` from `aspect_control`.
4. Create `resource/<package_name>` marker file.
5. Register in `setup.py` with `data_files` for launch files and resources.

### Adding a new ament_cmake package
1. CMake minimum 3.8.
2. Add `-Wall -Wextra -Wpedantic` compile options.
3. Include `ament_lint_auto` block in `BUILD_TESTING`.

---

## Git Conventions

- **Commit style:** Conventional Commits — `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- **Branch names:** `feature/<short-description>` or `fix/<short-description>`.
- **License:** Apache 2.0 — new source files need the Apache 2.0 header (copyright checks
  currently skipped, will be re-enabled).

---

## Git Workflow — Commit and Push Regularly

**Agents must commit and push to GitHub via SSH after every meaningful change.**

### When to commit
- After completing any discrete unit of work (new file, feature, bug fix, config change).
- After editing `AGENTS.md` or any `.docs/` planning document.
- Before switching tasks or ending a session.
- At minimum: after every 2–3 file changes, even if work is still in progress (use `wip:` prefix).

### How to commit and push

```bash
# Stage all changes not excluded by .gitignore
git add .

# Commit with a Conventional Commit message
git commit -m "feat: <short description>"

# Push via SSH (remote is already configured as git@github.com:bk-bf/aspect_rover.git)
git push origin main
```

### Verify SSH works
```bash
ssh -T git@github.com
# Expected: "Hi bk-bf! You've successfully authenticated..."
```

If SSH fails, do not fall back to HTTPS — fix the SSH key issue instead.

### Commit message prefixes
| Prefix | Use for |
|---|---|
| `feat:` | New functionality |
| `fix:` | Bug fix |
| `docs:` | Documentation / `.docs/` / `AGENTS.md` changes |
| `refactor:` | Code restructuring without behaviour change |
| `test:` | Test additions or fixes |
| `chore:` | Build, config, dependency changes |
| `wip:` | Work in progress — incomplete but worth persisting |

---

## Known Technical Debt

| Item | Location | Status |
|---|---|---|
| Copyright headers absent | All source files | Linter check skipped until headers added |
| cpplint disabled | `aspect_gazebo/CMakeLists.txt` | Re-enable once C++ code is added |
| `aspect_description` URDF stub | `urdf/aspect_rover.urdf.xacro` | Box geometry only — replace with real meshes |
| `aspect_control` teleop | `teleop_node.py` | termios keyboard loop implemented; joy input not yet added |
| EKF `/odometry/filtered` lag | bringup launch | Requires `/clock` to start; bridge lazy-connects; allow ~30 s warmup |

---

## Dependencies

```bash
# Inside the container
rosdep install --from-paths src --ignore-src -r -y
```

Key runtime: `rclpy`, `launch`, `launch_ros`, `ros_gz`, `robot_localization` (EKF).  
Key dev: `ament_flake8`, `ament_pep257`, `ament_lint_auto`, `uv`.
