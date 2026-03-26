# ASPECT Rover — Docker development image
# Base: ROS 2 Jazzy Jalisco (Ubuntu 24.04 Noble), LTS until May 2029
FROM osrf/ros:jazzy-desktop

# ── System packages ────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    gz-harmonic \
    ros-jazzy-ros-gz \
    ros-jazzy-joint-state-publisher-gui \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-xacro \
    ros-jazzy-rviz2 \
    curl \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# ── uv (Python tool runner — replaces pip/python directly) ────────────────────
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Dev tools installed via uv so they are version-pinned and reproducible
RUN uv tool install flake8 && \
    uv tool install pytest

# ── Workspace setup ────────────────────────────────────────────────────────────
RUN mkdir -p /workspace/src
WORKDIR /workspace

# GZ_SIM_RESOURCE_PATH lets the world SDF resolve model:// URIs without
# hardcoded absolute paths. Points to the installed package share directory.
ENV GZ_SIM_RESOURCE_PATH=/workspace/install/aspect_gazebo/share/aspect_gazebo

# Source ROS 2 and workspace overlay on every interactive shell
RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc && \
    echo "[ -f /workspace/install/setup.bash ] && source /workspace/install/setup.bash" \
    >> /root/.bashrc

# ── Entrypoint ─────────────────────────────────────────────────────────────────
# Source ROS 2 before any CMD so non-interactive invocations also work
COPY .docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
