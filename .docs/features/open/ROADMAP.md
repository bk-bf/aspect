<!-- LOC cap: 156 (source: 780, ratio: 0.20, updated: 2026-03-26) -->
<!-- Note: LOC cap relaxed for ROADMAP.md — full 8-year plan lives here -->
# ROADMAP

Current phase: **Phase 0** (2026 Q1). Completed items move to [`../archive/README.md`](../archive/README.md).

---

## Open

### Priority 1 — Phase 0: Make the Simulation Driveable

> Goal: wire up the full ROS 2 ↔ Gazebo loop so the rover can actually be driven
> in simulation. Currently the world launches but no model is spawned, no bridge
> connects `/cmd_vel` to the sim, and no drive plugin is in the SDF.
> Blocks everything in Phase 1.

- [x] T-007 [`aspect_bringup`]: Wire up `ros_gz_bridge` for `/cmd_vel` and `/odometry/filtered`
- [x] T-008 [`aspect_gazebo`]: Add differential drive plugin to `lunar_south_pole.world`
- [x] T-009 [`aspect_bringup`]: Spawn rover URDF model in simulation at launch
- [x] T-006 [`aspect_bringup`]: Add `robot_localization` EKF node to bringup launch

### Priority 2 — Phase 0: Complete Package Stubs

> Goal: finish the scaffolded nodes so the packages are functional, not just
> compilable. Copyright headers unblock the linter re-enable.

- [x] T-001 [`aspect_control`]: Implement keyboard input in `teleop_node.py` (termios raw mode)
- [x] T-002 [`aspect_navigation`]: Expose `/goto_waypoint` service in `simple_waypoint_nav.py`
- [x] T-003 [all]: Add Apache 2.0 copyright headers to all source files missing them
- [x] T-004 [all]: Re-enable `ament_copyright` linter check once T-003 is done
- [ ] T-005 [`aspect_description`]: Replace box geometry URDF with real rover meshes
- [ ] T-010 [`aspect_navigation`]: Add nav2 costmap + basic global planner

### Priority 3 — Phase 1: Simulation & AI (2026 Q2-Q3)

> Goal: rover autonomously excavates 50 g+ regolith in simulation at ≥ 80% success
> rate. TRL-3. Requires Priority 1 complete.

- [ ] T-101 [`aspect_navigation`]: Nav2 stack integration (costmap, global + local planner)
- [ ] T-102 [`aspect_description`]: Excavation scoop URDF + articulation joint
- [ ] T-103 [`aspect_gazebo`]: gymnasium environment wrapping Gazebo sim
- [ ] T-104: Baseline PPO training (SB3 Zoo defaults)
- [ ] T-105: Lunar terrain Nav2 parameter tuning
- [ ] T-106 [`aspect_bringup`]: Sensor fusion — wheel odometry + IMU via EKF validated in sim
- [ ] T-107: 30-minute stability test passing in CI

### Priority 4 — Phase 2: Hardware V1 + RL Production Training (2026 Q3–2027 Q1)

> Goal: physical 1:10 prototype driving in lab; RL policy achieving 20 g+ excavation
> in simulation. TRL-4. Cloud GPU budget ~$80.

- [ ] T-201: RPi 4B bring-up with ROS 2 Jazzy
- [ ] T-202: GY-521 IMU driver node
- [ ] T-203: Faulhaber 1524 / SG90 motor driver node
- [ ] T-204: ESP32-CAM ROS 2 video stream
- [ ] T-205: EKF fusion — wheel odometry + IMU on hardware
- [ ] T-206: Cloud GPU migration (Vast.ai / RunPod); checkpoint auto-save to HF Hub
- [ ] T-207: Hyperparameter search (SB3 Zoo ablations, 10 runs)
- [ ] T-208: Backyard excavation trial with regolith analog (≥ 5 g/min target)

### Priority 5 — Phase 3: Integrated ISRU Prototype (2027 Q2–2028 Q1)

> Goal: end-to-end water extraction demonstrated on bench. TRL-4 → TRL-5.
> 1:5 scale chassis. Cloud GPU budget ~$155. Requires T-208 field data.

- [ ] T-301: 1:5 scale chassis with Faulhaber motors throughout
- [ ] T-302: Heated auger thermal extraction subsystem
- [ ] T-303: Cold trap water capture system
- [ ] T-304: Small-scale electrolysis module (target: 1-5 g/hr H₂)
- [ ] T-305: Computer vision for ice-rich regolith detection
- [ ] T-306: Multi-scenario RL training (varied terrain, sensor noise, lighting)
- [ ] T-307: Domain randomisation for sim-to-real transfer
- [ ] T-308: > 50 g H₂O extraction per run validated

### Priority 6 — Phase 4: Extreme Environment Validation (2028)

> Goal: TRL-5. 72-hour autonomous operation demonstrated in Svalbard (-40 °C) and
> Atacama Desert. Requires funded partnerships for lab access.

- [ ] T-401: Sensor fusion for multi-modal data integration
- [ ] T-402: Fault-tolerant autonomous operation framework
- [ ] T-403: Arctic testing — Svalbard 168-hour continuous run
- [ ] T-404: Desert trials — Atacama thermal and solar validation
- [ ] T-405: Thermal-vacuum chamber testing at partner facility
- [ ] T-406: Full-scale (1:1) excavation subsystem (5-10 kg/hr regolith)

### Priority 7 — Phase 5: Scale-Up & Commercial Integration (2029)

> Goal: TRL-6. Mission-relevant performance metrics. H₂ production rate sufficient
> for propellant depot feasibility study. Requires $2-5M funding (SBIR/STTR).

- [ ] T-501: Full-scale system < 500 W total power consumption
- [ ] T-502: Partner with commercial electrolysis provider (OxEon or equiv. TRL-5+)
- [ ] T-503: Integrated system test: 10-20 g/hr H₂ production rate
- [ ] T-504: SBIR/STTR Phase I proposal submission

### Priority 8 — Phases 6-7: Mission Design & Lunar Demonstration (2030-2033)

> Goal: TRL-7-9. Secure CLPS contract; flight-qualify system; execute first robotic
> lunar H₂ production. Requires NASA/commercial contract. See
> [FEASIBILITY-2026.md](../../research/FEASIBILITY-2026.md) for funding pathway.

- [ ] T-601: NASA CLPS proposal (lunar surface demonstration)
- [ ] T-602: Flight-qualified design, mass budget < 100 kg
- [ ] T-603: Preliminary Design Review (PDR) with industry partners
- [ ] T-701: Engineering qualification model (EQM) manufacture
- [ ] T-702: Flight model (FM) + vibration/thermal-vac qualification
- [ ] T-703: Lunar surface ops: excavation → water extraction → electrolysis → H₂ storage
- [ ] T-704: Target: 1-5 kg total H₂ produced during 90-day surface mission

---

### Priority 2 (continued) — Phase 0: Complete Package Stubs

> Additional Phase 0 tasks surfaced during sprint planning. Not yet assigned T-NNN.

- [ ] [`aspect_gazebo`]: Process NASA LRO DEM data and generate Gazebo-compatible heightmap for South Pole region
- [ ] [`aspect_gazebo`]: Create `lunar_terrain.sdf` world with heightmap, lunar texture, and regolith physics
- [ ] [`aspect_description`]: Add IMU and camera Gazebo sensor plugins to `aspect_rover.urdf.xacro`
- [ ] [`aspect_bringup`]: Create `teleop_lunar.launch.py` integrating terrain world, rover spawn, and teleop node
- [ ] [`aspect_description`]: Create RViz2 config (`rover_view.rviz`) with TF, camera, odometry trail, IMU arrow
- [ ] [`aspect_navigation`]: Implement slope-based obstacle stop (>20°) in `simple_waypoint_nav.py`
- [ ] [`aspect_navigation`]: Add RViz2 interactive marker interface for waypoint setting
- [ ] [`aspect_navigation`]: Implement emergency stop + tilt detection (roll/pitch >30°) safety systems
- [ ] [all]: Write installation guide, architecture doc, and troubleshooting guide under `docs/`
- [ ] [all]: Record Phase 0 demonstration video and update README
