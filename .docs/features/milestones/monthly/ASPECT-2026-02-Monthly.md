# ASPECT February 2026 — Monthly Milestone

**Milestone:** Docker Environment + Lunar Terrain Simulation & Basic Rover Locomotion  
**Context:** Month 1 of Q1-Q2 "Simulation & AI" — Phase 0 infrastructure + Phase 1 foundation  
**Stack:** ROS 2 Jazzy + Gazebo Harmonic + Docker + rocker  
**Status:** In Progress (Week 1 of 4)  
**Yearly plan:** [ASPECT-2026-Yearly.md](../yearly/ASPECT-2026-Yearly.md)

---

## Monthly Objective

Establish Docker-based ROS 2 development environment and build functional lunar terrain
simulation. Demonstrate basic rover locomotion with collaborator-ready infrastructure.
Sets foundation for Nav2 integration (March), excavation AI (April), and testing (May).

**What gets built:** Docker containers + rocker workflow + ROS 2 workspace + Gazebo
lunar terrain + differential drive rover with sensors + teleoperation + GitHub CI/CD

---

## Success Criteria (Month-End Validation)

### Technical Targets
- [ ] Docker image builds and runs on CachyOS + any Linux with Docker
- [ ] rocker --x11 launches Gazebo GUI seamlessly (10-minute onboarding validated)
- [ ] Rover autonomously navigates to 5 sequential waypoints on lunar terrain
- [ ] 30+ minute stability test passes without crashes (inside container)
- [ ] Sensors publish at target rates: IMU (100 Hz), Camera (30 Hz), Odometry (50 Hz)
- [ ] Odometry drift < 5% over 50 m travel
- [ ] 15° slope navigation without tipping
- [ ] Simulation runs at 30+ FPS (rocker X11 forwarding)

### Infrastructure Targets
- [ ] GitHub Actions CI pipeline passes on every commit
- [ ] README demonstrates 10-minute collaborator onboarding
- [ ] Docker image < 5 GB compressed
- [ ] All ROS 2 packages build with zero warnings

### Documentation Targets
- [ ] Architecture diagram with all nodes/topics
- [ ] ROS 2 interface specs documented
- [ ] Docker troubleshooting guide (GPU passthrough, X11 forwarding)

### March Handoff
- [ ] Nav2 can be integrated (odometry + sensors working)
- [ ] Terrain suitable for SLAM/path planning testing
- [ ] Docker containers ready for cloud GPU migration (Phase 2)

---

## Deliverables

### 1. Docker Development Environment
- [ ] Dockerfile with ROS 2 Jazzy + Gazebo Harmonic
- [ ] docker-compose.yml for container orchestration
- [ ] rocker X11 forwarding functional on CachyOS
- [ ] GitHub Actions CI pipeline (automated builds)

**Week 1** | Any developer runs `docker build && rocker --x11` and sees Gazebo in < 10 min

---

### 2. Rover URDF Model (Basic)
- [ ] 4-wheel differential drive chassis
- [ ] IMU and camera sensor plugins
- [ ] Spawns in Gazebo with working physics

**Week 1-2** | Rover spawns via rocker, wheels rotate, sensors publish

---

### 3. Lunar Terrain Generation Pipeline
- [ ] NASA LRO DEM processed to heightmap
- [ ] Gazebo world file with 100 m × 100 m terrain
- [ ] Realistic surface properties (friction, material)

**Week 2** | Lunar terrain loads in container without physics glitches

---

### 4. Basic Locomotion System
- [ ] Differential drive controller
- [ ] Keyboard teleoperation
- [ ] Odometry from wheel encoders

**Week 2-3** | Rover controllable via keyboard (inside container), odometry tracks position

---

### 5. Sensor Integration & Visualization
- [ ] IMU data fusion for orientation
- [ ] Camera feed in RViz2
- [ ] TF tree configured correctly

**Week 3** | All sensor streams visible in RViz2 (via rocker), rosbag recording works

---

### 6. Basic Navigation Testing
- [ ] Waypoint navigation (manual setting)
- [ ] Basic obstacle avoidance
- [ ] 10+ test scenarios

**Week 3-4** | Rover reaches 5 waypoints autonomously, 30+ min stable

---

### 7. Documentation
- [ ] Setup guide (Docker → working sim in 10 minutes)
- [ ] Architecture diagram and node interfaces
- [ ] Test procedures
- [ ] Docker troubleshooting guide

**Week 4** | External dev can reproduce setup from docs alone (any Linux distro with Docker)

---

## Weekly Breakdown

**Week 1 (2026-02-15):** Foundation Setup → [ROADMAP.md](../../open/ROADMAP.md#week-1--february-15-21-2026)  
**Week 2 (2026-02-22):** Terrain & Locomotion → [ROADMAP.md](../../open/ROADMAP.md#week-2--february-22-28-2026)  
**Week 3 (2026-03-01):** Sensors & Navigation → [ROADMAP.md](../../open/ROADMAP.md#week-3--march-1-7-2026)  
**Week 4 (2026-03-08):** Testing & Docs → [ROADMAP.md](../../open/ROADMAP.md#week-4--march-8-14-2026)

---

## Risk Mitigation

| Risk | Mitigation | Week |
|---|---|---|
| Gazebo Harmonic instability | Budget debug time, fallback to Classic if critical | 1-2 |
| DEM terrain generation issues | Start with flat terrain, increment complexity | 2 |
| Week 1-2 setup delays | Docker + rocker (primary), pre-download base images | 1-2 |
| Documentation slips | Document incrementally, not batch at end | All |

---

## March Dependencies

**Must deliver by 2026-02-28:**
- Docker environment with rocker GUI working
- Working rover URDF with sensors
- Stable lunar terrain environment
- Basic locomotion + odometry
- ROS 2 workspace structure inside container

**Blocks March if incomplete:** Odometry (Nav2), sensor suite (SLAM), terrain (path planning)

---

## Progress Tracker

### Week 1 (Feb 15-21): In Progress
Environment setup, basic rover URDF

### Week 2 (Feb 22-28): Not Started
Lunar terrain, teleoperation

### Week 3 (Mar 1-7): Not Started
Sensors, waypoint navigation

### Week 4 (Mar 8-14): Not Started
Testing, documentation

---

## Month-End Review

**Completed:** [List deliverables 1-7 status]  
**Challenges:** [What took longer/was harder than expected]  
**Carryover:** [Tasks rolling to March]  
**March Readiness:** Low / Medium / High
