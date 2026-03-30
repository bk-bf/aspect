---
status: active
updated: 2026-03-30
---
# ASPECT — Autonomous Surface Precision Excavation for Celestial Terrain

A ROS 2 Jazzy + Gazebo Harmonic simulation and physical prototype of a lunar mining
rover for in-situ resource utilization (ISRU), with progressive testing from simulation
to extreme Earth environments.

## Project Goals

- Simulation-to-hardware pipeline for lunar regolith excavation using ROS 2 Jazzy and
  Gazebo Harmonic terrain modelling
- 1:10 scale rover prototype: > 5 g/min regolith analog excavation at < 50 W
- Progressive testing: simulation → backyard → Svalbard (-40 °C) → Atacama Desert
- TRL-3 → TRL-6 by 2028; foundation for lunar hydrogen production (10 t/yr by 2032)

## System Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for package diagram and data flow.

**Simulation:** ROS 2 Jazzy Jalisco + Gazebo Harmonic, Docker + rocker for GUI  
**Hardware:** 1:10 scale, 3D-printed PETG/PLA+, RPi 4B, GY-521 IMU, ESP32-CAM, Faulhaber 1524 motors

## Documentation Index

| Doc | Purpose |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Package layout, data flow, interfaces |
| [PHILOSOPHY.md](PHILOSOPHY.md) | Guiding principles and scope boundaries |
| [DECISIONS.md](DECISIONS.md) | Architectural decisions D-001 through D-012 |
| [features/open/ROADMAP.md](features/open/ROADMAP.md) | Open tasks T-001 through T-704 |
| [bugs/BUGS.md](bugs/BUGS.md) | Known defects B-000 through B-018 |
| [research/FEASIBILITY-2026.md](research/FEASIBILITY-2026.md) | Market/funding feasibility analysis |
| [tasks/yearly/ASPECT-2026-Yearly.md](tasks/yearly/ASPECT-2026-Yearly.md) | 2026 yearly milestones |
| [tasks/monthly/](tasks/monthly/) | Monthly sprint milestones |
| [tasks/weekly/](tasks/weekly/) | Weekly task logs |

## Installation

See the main [README](../README.md) for the Docker-based quick start.

## License

Apache 2.0 — see [LICENSE](../LICENSE).
