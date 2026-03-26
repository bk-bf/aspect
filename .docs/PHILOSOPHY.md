<!-- LOC cap: 156 (source: 780, ratio: 0.20, updated: 2026-03-26) -->
# PHILOSOPHY

## Goal

Build a lunar regolith excavation rover that reaches TRL-6 by 2028 — from simulation
through Arctic analog testing — as a solo hobby project with collaborator-ready
infrastructure from day one.

Target metric: autonomous excavation ≥ 5 g/min at < 50 W on lunar regolith analog.

## Principles

**Simulation first.** Every hardware capability is proven in Gazebo Harmonic before
being built. A physical prototype that can't be validated in simulation is not built.

**Reproducibility over convenience.** Docker-first development means any contributor
can run `docker compose up` and have a working environment in under 10 minutes.
Nothing is installed on the host outside of Docker and `uv`.

**Simplicity over completeness.** Prefer a minimal working system over a feature-rich
broken one. Stubs with clear TODOs are acceptable; hidden complexity is not. The
URDF is boxes until it needs to be meshes. The nav controller is proportional until
it needs to be something else.

**Metrics drive decisions.** `val_bpb` for ML experiments; excavation g/min and W for
hardware. No subjective "feels better" — measure it.

**LTS stack, long timeline.** ROS 2 Jazzy (EOL 2029) was chosen to avoid a forced
migration during hardware integration in Phase 3. Eight-year timelines demand
infrastructure that outlasts trends.

**Open by default.** Apache 2.0 license. NASA Open-Source Rover as physical baseline.
ESA/NASA ISRU standards as performance benchmarks. Code and docs version-controlled
together.

## What this project is not

- Not a commercial product or startup — hobby project timeline, hobby project budget.
- Not aiming to reinvent ROS 2 primitives — use nav2, robot_localization, ros_gz as-is.
- Not GPU-first (Phase 0-1) — RL training on cloud GPU is Phase 2+ only.
