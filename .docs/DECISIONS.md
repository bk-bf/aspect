<!-- LOC cap: 156 (source: 780, ratio: 0.20, updated: 2026-03-26) -->
<!-- Note: LOC cap relaxed for DECISIONS.md — decisions log grows over time by design -->
# DECISIONS

Architecture and tooling decisions with rationale. Append new entries; do not edit
past decisions.

---

## D-001 — ROS 2 Jazzy over Humble

**Date:** 2026-02-15  
**Status:** Active

**Decision:** Use ROS 2 Jazzy Jalisco (LTS, EOL May 2029) as the ROS distribution.

**Rationale:** Humble EOL is May 2027 — only 15 months from project start, forcing a
migration during Phase 3 hardware integration. Jazzy covers the full 2026-2029 window.
Ubuntu 24.04 Noble native support; official Gazebo Harmonic integration with no
workarounds required.

**Rejected:** ROS 2 Humble Hawksbill — EOL too soon, Harmonic support unofficial.

---

## D-002 — Gazebo Harmonic over Gazebo Classic

**Date:** 2026-02-15  
**Status:** Active

**Decision:** Use Gazebo Harmonic as the simulation platform.

**Rationale:** Gazebo Classic EOL January 2025. Harmonic is the official ROS 2 Jazzy
target (`ros-jazzy-ros-gz`). Supports headless server mode for future cloud GPU RL
training. Modern physics (DART).

**Rejected:** Gazebo Classic — already deprecated; Fortress — EOL September 2024.

---

## D-003 — Docker-first development

**Date:** 2026-02-15  
**Status:** Active

**Decision:** All ROS 2 / Gazebo work runs inside the Docker container
(`osrf/ros:jazzy-desktop` base). `rocker` for GUI passthrough; `docker compose` for
headless.

**Rationale:** Eliminates host-OS dependency issues (CachyOS AUR instability caused
the 2025 plan failure). Any collaborator runs one command to get a working environment.
Enables identical local and cloud execution.

---

## D-004 — uv as Python tool runner

**Date:** 2026-02-15  
**Status:** Active

**Decision:** Use `uv` for all Python invocations outside colcon's build graph. Never
use bare `python`, `python3`, or `pip`.

**Rationale:** Reproducible environments via `uv.lock`; fast dependency resolution;
official `uv tool run` pattern for linting tools (`flake8`, `pydocstyle`). `colcon`
manages its own Python env and is not interfered with.

---

## D-005 — model:// URIs for Gazebo assets

**Date:** 2026-03-08  
**Status:** Active

**Decision:** World SDF files use `model://` URIs resolved via `GZ_SIM_RESOURCE_PATH`.
No hardcoded absolute paths anywhere in SDF or launch files.

**Rationale:** Absolute paths break when the repo is cloned to a different location or
run inside Docker at `/workspace`. `GZ_SIM_RESOURCE_PATH` is set in the Dockerfile and
documented for out-of-container use.

---

## D-006 — Proportional controller for Phase 0 navigation

**Date:** 2026-03-08  
**Status:** Active

**Decision:** `simple_waypoint_nav.py` uses a proportional heading + distance
controller rather than nav2/SLAM.

**Rationale:** nav2 requires a costmap, sensor setup, and parameter tuning that is
out of scope for Phase 0. The P-controller is sufficient for open-loop waypoint
following in simulation and provides a testable baseline. nav2 integration is a
Phase 1 task.

---

## D-007 — RL training framework: gymnasium + stable-baselines3

**Date:** 2026-02-15  
**Status:** Planned (Phase 2+)

**Decision:** Use `gymnasium` + `stable-baselines3` (SB3) + PyTorch for reinforcement
learning. Extend with SB3 Contrib (TQC, RecurrentPPO) and RL Baselines3 Zoo for
pre-tuned hyperparameters.

**Rationale:** SB3 Zoo eliminates months of hyperparameter search. Contrib algorithms
handle partial observability from sensor noise. Industry standard with excellent
documentation. Not needed until Phase 2 — no RL code in the repo yet.

---

## D-008 — Cloud GPU over local GPU for RL training

**Date:** 2026-02-15  
**Status:** Planned (Phase 2+)

**Decision:** Rent cloud GPU (Vast.ai RTX 4090 at ~$0.25/hr, or RunPod A4000 at
~$0.17/hr) rather than purchasing dedicated hardware.

**Rationale:** Realistic annual budget ~$235 (930 GPU hours). Purchasing an RTX 4090
costs ~$1,600 — 7× more expensive for Phase 2-3 workloads. Cloud instances are
preemptible with hourly checkpointing. Budget alerts at $100/$200/$300.

**Rejected:** Buying RTX 4090 — cost-inefficient for hobby project GPU hours; using
the TX2540m1 server CPU — viable fallback but too slow for production RL training.

---

## D-011 — Gazebo server-only mode (`-s`) as default in launch file

**Date:** 2026-03-26  
**Status:** Active

**Decision:** `launch_lunar_south_pole.py` runs `gz sim -s -v 4 <world>` (server-only,
no GUI). The simulation starts **paused**; unpause with:

```bash
gz service -s /world/lunar_south_pole/control \
  --reqtype gz.msgs.WorldControl --reptype gz.msgs.Boolean \
  --timeout 5000 --req 'pause: false'
```

**Rationale:** `gz sim` normally starts GUI and physics server in a single process.
In a headless container (no GPU, no display), the Qt/OGRE GUI thread crashes and takes
the physics server down with it (SIGKILL). Server-only mode (`-s`) skips the GUI
entirely and is the correct approach for the autoresearcher headless CI environment.
For interactive GUI use, `rocker --x11` on the host is the documented workflow.

**Rejected:** Running `gz sim` without `-s` in the container — GUI crash reproducibly
kills the physics server; Xvfb virtual display does not satisfy OGRE's shader requirements.

---

## D-009 — Model storage on Hugging Face Hub

**Date:** 2026-02-15  
**Status:** Planned (Phase 2+)

**Decision:** Store trained RL model checkpoints on Hugging Face Hub (free, 50 GB
private). Training data on S3-compatible storage (Backblaze B2 at $5/TB/month).

**Rationale:** Git LFS free tier (1 GB) is too small for RL checkpoints. Hugging Face
Hub is designed for model versioning. Backblaze B2 is ~4.6× cheaper than AWS S3
($5 vs $23/TB/month).

---

## D-010 — Compress simulation-only phase; parallel hardware prototyping

**Date:** 2026-02-15  
**Status:** Active

**Decision:** Simulation-only phase capped at 6-8 weeks; physical 1:10 prototype
development begins in parallel during Phase 2, not after simulation is "complete".

**Rationale:** NASA Lunabotics 2025 winners (University of Utah) emphasised aggressive
early hardware testing: "test early, test hard, break it to understand where it
breaks." Sim-to-real gap is best discovered early. Over-optimising for Gazebo physics
(which ≠ real regolith) wastes time.

**Rejected:** 10-week simulation-only phase — delays hardware feedback, risks
discovering sim-to-real gap too late in the project.
