"""Launch the ASPECT rover waypoint navigation node."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for waypoint navigation."""
    return LaunchDescription([
        Node(
            package='aspect_navigation',
            executable='simple_waypoint_nav',
            name='simple_waypoint_nav',
            output='screen',
            parameters=[{
                'acceptance_radius': 0.5,
                'linear_speed': 0.2,
                'angular_speed': 0.5,
            }],
        ),
    ])
