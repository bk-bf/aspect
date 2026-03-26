"""Launch the ASPECT rover teleop node."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for teleoperation."""
    return LaunchDescription([
        Node(
            package='aspect_control',
            executable='teleop_node',
            name='teleop_node',
            output='screen',
            emulate_tty=True,
        ),
    ])
