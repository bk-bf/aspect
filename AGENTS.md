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
# Launch lunar south pole simulation
ros2 launch aspect_bringup launch_lunar_south_pole.py

# Launch with a custom world path
ros2 launch aspect_bringup launch_lunar_south_pole.py world:=/path/to/world.sdf

# View rover URDF in RViz2
ros2 launch aspect_description view_urdf.launch.py

# Teleoperation node
ros2 launch aspect_control teleop.launch.py

# Waypoint navigation node
ros2 launch aspect_navigation waypoint_nav.launch.py
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

## Known Technical Debt

| Item | Location | Status |
|---|---|---|
| Copyright headers absent | All source files | Linter check skipped until headers added |
| cpplint disabled | `aspect_gazebo/CMakeLists.txt` | Re-enable once C++ code is added |
| `aspect_description` URDF stub | `urdf/aspect_rover.urdf.xacro` | Box geometry only — replace with real meshes |
| `aspect_control` teleop incomplete | `teleop_node.py` | Needs keyboard/joy input implementation |
| `aspect_navigation` service missing | `simple_waypoint_nav.py` | `/goto_waypoint` service not yet implemented |

---

## Dependencies

```bash
# Inside the container
rosdep install --from-paths src --ignore-src -r -y
```

Key runtime: `rclpy`, `launch`, `launch_ros`, `ros_gz`, `robot_localization` (EKF).  
Key dev: `ament_flake8`, `ament_pep257`, `ament_lint_auto`, `uv`.
