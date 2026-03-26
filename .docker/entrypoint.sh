#!/bin/bash
# Docker entrypoint — sources ROS 2 and workspace overlay before running CMD
set -e

source /opt/ros/jazzy/setup.bash

if [ -f /workspace/install/setup.bash ]; then
    source /workspace/install/setup.bash
fi

exec "$@"
