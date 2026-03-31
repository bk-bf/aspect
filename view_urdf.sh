#!/usr/bin/env bash
# view_urdf.sh — headless URDF visualiser via self-hosted Foxglove Studio
# Run from the repo root on the VPS (or any host with Docker).
# Usage: bash view_urdf.sh [--worktree <name>] [--port <port>] [--ui-port <port>]
#
# Opens two containers:
#   aspect:jazzy        → foxglove_bridge  on FOXGLOVE_PORT (default 8765)
#   ghcr.io/foxglove/studio → web UI        on UI_PORT       (default 8080)
#
# Connect: http://<host>:8080  →  Open Connection → ws://<host>:8765
# On Tailscale: http://<machine>.ts.net:8080

set -eo pipefail

FOXGLOVE_PORT=8765
UI_PORT=8080
WORKTREE_NAME=""
INSIDE_CONTAINER=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --worktree)
            [[ -z "${2:-}" ]] && { echo "ERROR: --worktree requires a name"; exit 1; }
            WORKTREE_NAME="$2"; shift 2 ;;
        --port)    FOXGLOVE_PORT="$2"; shift 2 ;;
        --ui-port) UI_PORT="$2";       shift 2 ;;
        --inside-container) INSIDE_CONTAINER=true; shift ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

# ── inside container: build if needed, then launch bridge ─────────────────────
if $INSIDE_CONTAINER; then
    if ! ros2 pkg list 2>/dev/null | grep -q foxglove_bridge; then
        echo "==> Installing foxglove_bridge (one-time, rebuild image to skip)..."
        apt-get update -qq && apt-get install -y -qq ros-jazzy-foxglove-bridge \
            && rm -rf /var/lib/apt/lists/*
    fi

    if [[ ! -f install/setup.bash ]]; then
        echo "==> No install/ found — building workspace (first run, ~2 min)..."
        colcon build --symlink-install 2>&1 | grep -E "^\[|^(Summary|ERROR)" || true
    else
        colcon build --symlink-install --packages-select aspect_description \
            2>&1 | grep -E "^\[|^(Summary|ERROR)" || true
    fi
    # shellcheck source=/dev/null
    set +u; source install/setup.bash; set -u

    exec ros2 launch aspect_description foxglove_urdf.launch.py \
        port:="${FOXGLOVE_PORT}"
fi

# ── host side ─────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -n "$WORKTREE_NAME" ]]; then
    WORKSPACE="$SCRIPT_DIR/features/$WORKTREE_NAME"
    [[ -d "$WORKSPACE" ]] || { echo "ERROR: worktree not found: $WORKSPACE"; exit 1; }
else
    WORKSPACE="$SCRIPT_DIR"
fi

DOCKER="docker"
if ! docker info &>/dev/null 2>&1; then
    DOCKER="sudo docker"
fi

# ── docker daemon lifecycle ────────────────────────────────────────────────────
STARTED_DOCKER=false
if [[ "$(uname -s)" == "Linux" ]] && ! $DOCKER info &>/dev/null 2>&1; then
    echo "Docker daemon not running — starting it..."
    sudo systemctl start docker
    for _i in $(seq 1 10); do $DOCKER info &>/dev/null 2>&1 && break; sleep 1; done
    STARTED_DOCKER=true
fi

UI_CONTAINER=""
cleanup() {
    [[ -n "$UI_CONTAINER" ]] && $DOCKER stop "$UI_CONTAINER" &>/dev/null || true
    if [[ "$STARTED_DOCKER" == true ]]; then
        echo "Stopping Docker daemon (we started it)..."
        sudo systemctl stop docker docker.socket
    fi
}
trap cleanup EXIT

# ── ensure bridge image exists ────────────────────────────────────────────────
if ! $DOCKER image inspect aspect:jazzy &>/dev/null 2>&1; then
    echo "Image 'aspect:jazzy' not found — building (~10 min first time)..."
    $DOCKER build -f "$SCRIPT_DIR/.docker/Dockerfile" -t aspect:jazzy "$SCRIPT_DIR"
fi

# ── kill leftover containers on those ports ───────────────────────────────────
for _port in "$FOXGLOVE_PORT" "$UI_PORT"; do
    _existing=$($DOCKER ps -q --filter "publish=${_port}" 2>/dev/null || true)
    [[ -n "$_existing" ]] && $DOCKER stop $_existing >/dev/null && \
        echo "Stopped existing container on port ${_port}."
done

# ── start self-hosted Foxglove Studio UI (background) ─────────────────────────
echo "Starting Foxglove Studio UI on port ${UI_PORT}..."
UI_CONTAINER=$($DOCKER run -d --rm \
    -p "0.0.0.0:${UI_PORT}:8080" \
    ghcr.io/foxglove/studio:latest)

HOST="$(hostname -s)"
echo ""
echo "  Foxglove Studio : http://${HOST}.ts.net:${UI_PORT}"
echo "  Bridge URL       : ws://${HOST}.ts.net:${FOXGLOVE_PORT}"
echo ""
echo "  In the UI: Open Connection → Foxglove WebSocket → ws://${HOST}.ts.net:${FOXGLOVE_PORT}"
echo ""
echo "Press Ctrl+C to stop."
echo ""

$DOCKER run --rm -it \
    -p "0.0.0.0:${FOXGLOVE_PORT}:${FOXGLOVE_PORT}" \
    -v "$WORKSPACE":/workspace \
    -w /workspace \
    aspect:jazzy \
    bash /workspace/view_urdf.sh --inside-container --port "${FOXGLOVE_PORT}"

