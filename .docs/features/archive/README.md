<!-- LOC cap: 156 (source: 780, ratio: 0.20, updated: 2026-03-26) -->
# Archived Features

Completed roadmap items are moved here from
[`../open/ROADMAP.md`](../open/ROADMAP.md).

| ID | Completed | Description |
|---|---|---|
| — | 2026-03-26 | Initial scaffold: all 5 packages created (`aspect_bringup`, `aspect_description`, `aspect_control`, `aspect_navigation`, `aspect_gazebo`) |
| — | 2026-03-26 | Docker infrastructure: `Dockerfile`, `docker-compose.yml`, `entrypoint.sh` |
| — | 2026-03-26 | World SDF upgraded from SDF 1.4 to SDF 1.9 (Gazebo Harmonic) |
| — | 2026-03-26 | Hardcoded absolute paths removed; `model://` URIs + `GZ_SIM_RESOURCE_PATH` adopted |
| — | 2026-03-26 | `gz sim` CLI replacing deprecated `ign gazebo` |
| — | 2026-03-26 | Docs migrated: planning docs moved from repo root into `.docs/` |

## Deferred

Items explicitly deferred — not abandoned, but blocked on an external prerequisite
or deliberately postponed until a later phase.

| ID | Deferred | Prerequisite to revisit | Description |
|---|---|---|---|
| T-005 | 2026-03-29 | Phase 2 hardware design finalised (real chassis dimensions known) | [`aspect_description`] Replace box geometry URDF with real rover meshes |
