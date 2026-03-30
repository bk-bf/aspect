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
**Status:** Active (partially superseded by D-012 for nav2 costmap)

**Decision:** `simple_waypoint_nav.py` uses a proportional heading + distance
controller rather than nav2/SLAM.

**Rationale:** nav2 requires a costmap, sensor setup, and parameter tuning that is
out of scope for Phase 0. The P-controller is sufficient for open-loop waypoint
following in simulation and provides a testable baseline. Full nav2 integration
(local planner, DWB, SLAM) remains a Phase 1 task (T-101); the Phase 0 nav2 costmap
+ global planner addition is captured in D-012.

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

## D-008 — GPU compute strategy for RL training

**Date:** 2026-02-15 (revised 2026-03-29)  
**Status:** Planned (Phase 2+)

**Decision:** Rent cloud GPU rather than purchasing hardware. Do not activate paid
compute until all three gates are met:
1. T-104 CPU proof-of-concept complete — gym env and reward function validated locally
2. T-206 checkpoint auto-save to HF Hub working — no training run can be lost
3. A single 1-hour test run on Vast.ai confirms the Docker image trains correctly
   before committing to a full hyperparameter search budget

**Evaluation order (cheapest → most capable):**

| Option | Cost | Notes |
|---|---|---|
| Kaggle / Colab free tier | $0 | Max 12 hr/session — sufficient for T-104 CPU PoC |
| University HPC (borrowed) | $0 | Check availability first; good if accessible within 1 week |
| Vast.ai RTX 4090 spot | ~$0.25/hr | Preferred for T-207; preemptible, hourly checkpoint required |
| RunPod A4000 on-demand | ~$0.17/hr | Fallback if Vast.ai spot unavailable; slightly slower |
| Buy RTX 4090 | ~$1,600 | Rejected — see below |

**Budget gate:** Phase 2 GPU spend capped at $80; alert at $40 and $70.
Do not start T-207 until the $80 budget is confirmed available.

**Rationale:** Annual budget ~$235 (930 GPU hours). Purchasing an RTX 4090 costs
~$1,600 — 7× more expensive for Phase 2-3 workloads. The free-tier path covers T-104,
delaying real spend until the training pipeline is proven. Renting before T-206
checkpoint save is working risks losing entire runs to preemption.

**Rejected:** Buying RTX 4090 — cost-inefficient for hobby-scale GPU hours; using the
TX2540m1 server CPU for production training — too slow for T-207 hyperparameter search.

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

---

## D-012 — Partial nav2 integration pulled into Phase 0 (T-010)

**Date:** 2026-03-30  
**Status:** Active

**Decision:** Pull nav2 global costmap + NavFn global planner + BT navigator into
Phase 0 as T-010, alongside the proportional P-controller (D-006). Full nav2
integration (local planner DWB, SLAM, parameter tuning) remains Phase 1 (T-101).

**Rationale:** The global costmap and planner are relatively low-overhead to wire up
(config file + launch file; no sensor tuning). Having them in place in Phase 0 lets
Phase 1 work start from a functioning nav2 skeleton rather than from scratch, reducing
Phase 1 integration risk. The P-controller remains the active autonomous navigation
path; nav2 is wired but not the primary control loop until T-101.

**Rejected:** Deferring all nav2 to Phase 1 — creates a larger Phase 1 integration
cliff; the costmap config is cleaner to write while the simulation is being stood up.

---

## D-013 — Excavation Mechanism: Auger as Canonical

**Date:** 2026-03-30  
**Status:** Active

**Decision:** Auger (continuous helical drill + vertical feed) is the canonical
excavation mechanism for ASPECT. Scoop arm and bucket drum designs are deferred
to a competition fork (D-015) only.

**Rationale:** 2 DOF only (rotation + prismatic feed) vs. 3–5 for a scoop arm —
simpler URDF, RL action space, and real hardware. Sub-surface access (0.5–2 m depth)
is required for ice-bearing regolith at the lunar south pole; surface scoops reach
only the radiation-baked dry top layer. Torsional reaction force is manageable via
wide wheelbase with no complex counter-rotation mechanism at 1:10 scale. Directly
pre-adapts T-302 (Phase 3 heated auger thermal extraction) — the auger body becomes
the extraction subsystem with resistive heating added to the flights. Reference
architecture: NASA LADI (Lunar Auger Dryer ISRU), AIAA 2023-4758.

**Non-goal:** High-volume surface regolith throughput (Lunabotics-style metric). For
that use case, see D-015 (competition fork).

**Rejected:** Scoop arm — higher DOF, surface access only; bucket drum —
counter-rotation mechanism adds hardware complexity at 1:10 scale.

---

## D-014 — Chassis Design Constraint: Auger Torque Reaction

**Date:** 2026-03-30  
**Status:** Active

**Decision:** Wheelbase must be wide enough that (torque arm × wheel normal force)
exceeds maximum auger reaction torque at nominal RPM. Validated in T-105 (terrain
parameter tuning). Final wheelbase spec documented in `aspect_description` before
T-201 (RPi bring-up) so the hardware build matches sim geometry.

**Rationale:** The auger's torsional reaction torque during drilling attempts to
rotate the rover body counter to the auger spin direction. On loose low-gravity
regolith, wheel traction is the primary resistive force. Spec must be locked before
hardware fabrication begins.

---

## D-015 — Competition Fork Strategy: Lunabotics Variant

**Date:** 2026-03-30  
**Status:** Planned (if Lunabotics opportunity confirmed)

**Decision:** If a Lunabotics-style competition (judged on bulk regolith mass
deposited) becomes a target, fork `aspect_description` and `aspect_gazebo` only.
The nav, control, AI, and bringup stack is mechanism-agnostic and shared unchanged.

**Fork scope (~3–4 files):**
- `aspect_description/urdf/` — replace auger URDF with bucket drum (RASSOR-style,
  counter-rotating for zero net torque reaction; reference: EZ-RASSOR open source)
- `aspect_gazebo/worlds/` — swap lunar south pole world with flat competition arena
- `aspect_navigation/` — swap reward function: `mass_deposited` replaces
  `water_yield`; Nav2 params identical
- Keep `/excavation/cmd` ROS 2 topic interface identical so fork stays shallow

**Implementation cost:** ~1 weekend once T-103 gym env is stable. No roadmap tasks
created until opportunity is confirmed.

**Rejected:** Full fork of nav/AI/bringup stack — unnecessary; the
mechanism-agnostic interface design means only description and world files change.

---

## D-016 — AI Stack Architecture: Three-Tier Hierarchical Control

**Date:** 2026-03-30  
**Status:** Planned (Phase 2)

**Decision:** Adopt a three-tier hierarchical control architecture replacing the
flat PPO→Nav2 design.

- **Tier 1 — Reactive (< 10 ms):** Nav2 + EKF, cliff detection, safety reflexes
- **Tier 2 — Manipulation (< 50 ms):** VLA policy (OpenVLA-OFT, LoRA fine-tuned
  on Gazebo rollouts) — camera frame + goal text → `[v_x, ω_z, θ_auger]` action tokens
- **Tier 3 — Planning (< 2 s):** LLM task planner (Qwen2.5-7B or Gemma-3 via
  Ollama) — symbolic mission state → task commands; text↔action overhead quarantined
  here where latency budget is acceptable

**PPO role:** Retained as reward-function validator (T-104) and rollout data
generator for VLA fine-tuning (T-AI-01). Not the production policy.

**Multi-rover:** Mesh-first (T-AI-06, Phase 3); satellite relay deferred to Phase 5+.

**Model choice:** OpenVLA-OFT (7B, LoRA) as default. Re-evaluate against alternatives
at T-AI-01 completion (Q3 2026).

**Rejected:** Flat PPO production policy — text serialisation overhead from LLM
planner is unacceptable at < 50ms; VLA handles the manipulation tier more
sample-efficiently than PPO for camera-based tasks.
