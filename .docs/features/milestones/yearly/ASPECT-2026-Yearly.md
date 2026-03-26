# ASPECT 2026 Yearly Milestones

**Tech stack:** ROS 2 Jazzy + Gazebo Harmonic + Docker + Python/C++  
**Year goal:** Build and field-test a functional 1:10 scale autonomous lunar rover prototype capable of regolith excavation.  
**Architecture:** Docker-first development with rocker for GUI; cloud GPU for RL training (Phases 2-3). See [DECISIONS.md](../../DECISIONS.md).

---

## Q1-Q2: Simulation & AI (Feb-Jun)

**What:** Build Gazebo Harmonic lunar terrain simulation + excavation AI using RL/MPC  
**Outcome:** Rover autonomously excavates 50 g+ regolith in simulation with ≥ 80% success rate  
**Monthly:** [Feb](../monthly/ASPECT-2026-02-Monthly.md)

---

## Q2-Q3: Software & Hardware Integration (May-Aug)

**What:** Deploy software stack to Raspberry Pi 4B+, integrate sensors (IMU, cameras), build electronics bay  
**Outcome:** Software runs on target hardware, sensor fusion working, ready for mechanical integration

---

## Q3-Q4: Physical Prototype & Field Testing (Jul-Dec)

**What:** Fabricate 1:10 rover chassis, assemble excavation mechanism, conduct outdoor field tests in analog terrain  
**Outcome:** Functional prototype demonstrates autonomous excavation in real-world conditions

---

## Key Risks & Mitigation

| Risk | Impact | Mitigation | Timeline |
|---|---|---|---|
| Component availability | High | Order long-lead items (motors) early | Q2 start |
| Hardware build complexity | High | Allocate 4-6 week buffer for Milestone 3 | Sep-Oct |
| Weather-dependent testing | Medium | Plan indoor backup testing | Q4 |
| Milestone 1 delays | Medium | Software/hardware work can proceed in parallel | 2-3 week buffer |

---

## 2026 Year-End Success Criteria

**Primary goal:** TRL-2 → TRL-4  
**Deliverable:** Working 1:10 prototype with autonomous excavation capability + demonstration video

**Minimum acceptable:**
- Simulation environment functional (Milestone 1)
- Software runs on hardware (Milestone 2)
- 1:10 prototype built and tested outdoors (Milestone 3)
- 50 g regolith excavated in single autonomous mission

**Stretch goals:**
- 100 g+ regolith per mission
- 2-hour autonomous missions
- Harsh environment testing (-20 °C or +50 °C)
- Begin thermal extraction simulation (head start on 2027)
