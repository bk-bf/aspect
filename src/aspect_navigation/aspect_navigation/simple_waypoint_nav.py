# Copyright 2026 Kirill Boychenkov
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Simple proportional waypoint navigation node for the ASPECT rover."""

import math

from aspect_msgs.srv import GotoWaypoint
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node


class SimpleWaypointNav(Node):
    """Navigate the rover to a (x, y) waypoint using proportional control.

    Subscribes to filtered odometry, publishes velocity commands, and
    exposes a ``/goto_waypoint`` service.

    Topics
    ------
    Subscribers:
        /odometry/filtered (nav_msgs/Odometry) — current pose from EKF
    Publishers:
        /cmd_vel (geometry_msgs/Twist) — velocity commands

    Services
    --------
        /goto_waypoint (aspect_msgs/GotoWaypoint) — set a navigation goal

    Parameters
    ----------
    acceptance_radius : float
        Distance in metres at which a waypoint is considered reached (default 0.5).
    linear_speed : float
        Maximum forward speed in m/s (default 0.2).
    angular_speed : float
        Maximum rotational speed in rad/s (default 0.5).
    """

    def __init__(self) -> None:
        """Initialise waypoint nav node, subscribers, publisher, and service."""
        super().__init__('simple_waypoint_nav')

        self.declare_parameter('acceptance_radius', 0.5)
        self.declare_parameter('linear_speed', 0.2)
        self.declare_parameter('angular_speed', 0.5)

        self._acceptance_radius: float = (
            self.get_parameter('acceptance_radius').get_parameter_value().double_value
        )
        self._linear_speed: float = (
            self.get_parameter('linear_speed').get_parameter_value().double_value
        )
        self._angular_speed: float = (
            self.get_parameter('angular_speed').get_parameter_value().double_value
        )

        self._goal_x: float | None = None
        self._goal_y: float | None = None
        self._current_x: float = 0.0
        self._current_y: float = 0.0
        self._current_yaw: float = 0.0

        self._odom_sub = self.create_subscription(
            Odometry, '/odometry/filtered', self._odom_callback, 10
        )
        self._cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self._goto_srv = self.create_service(
            GotoWaypoint, '/goto_waypoint', self._goto_waypoint_callback
        )

        self.get_logger().info('SimpleWaypointNav started — /goto_waypoint service ready')

    def _goto_waypoint_callback(
        self, request: GotoWaypoint.Request, response: GotoWaypoint.Response
    ) -> GotoWaypoint.Response:
        """Handle incoming /goto_waypoint service requests.

        Parameters
        ----------
        request:
            Service request containing target x and y coordinates.
        response:
            Service response indicating success and a status message.
        """
        self.set_goal(request.x, request.y)
        response.success = True
        response.message = f'Goal set to ({request.x:.2f}, {request.y:.2f})'
        return response

    def _odom_callback(self, msg: Odometry) -> None:
        """Handle incoming odometry messages and update position."""
        self._current_x = msg.pose.pose.position.x
        self._current_y = msg.pose.pose.position.y

        # Extract yaw from quaternion
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self._current_yaw = math.atan2(siny_cosp, cosy_cosp)

        if self._goal_x is not None and self._goal_y is not None:
            self._navigate_to_goal()

    def set_goal(self, x: float, y: float) -> None:
        """Set a new navigation goal.

        Parameters
        ----------
        x:
            Target x-coordinate in the odom frame (metres).
        y:
            Target y-coordinate in the odom frame (metres).
        """
        self._goal_x = x
        self._goal_y = y
        self.get_logger().info(f'New goal set: ({x:.2f}, {y:.2f})')

    def _navigate_to_goal(self) -> None:
        """Compute and publish velocity toward the current goal."""
        assert self._goal_x is not None and self._goal_y is not None
        dx = self._goal_x - self._current_x
        dy = self._goal_y - self._current_y
        distance = math.hypot(dx, dy)

        if distance < self._acceptance_radius:
            self._stop()
            self.get_logger().info('Goal reached')
            self._goal_x = None
            self._goal_y = None
            return

        target_angle = math.atan2(dy, dx)
        angle_error = target_angle - self._current_yaw

        # Normalise angle to [-pi, pi]
        while angle_error > math.pi:
            angle_error -= 2.0 * math.pi
        while angle_error < -math.pi:
            angle_error += 2.0 * math.pi

        cmd = Twist()
        cmd.angular.z = max(
            -self._angular_speed,
            min(self._angular_speed, angle_error)
        )
        if abs(angle_error) < 0.3:  # Drive forward only when roughly aligned
            cmd.linear.x = self._linear_speed
        self._cmd_pub.publish(cmd)

    def _stop(self) -> None:
        """Publish a zero-velocity command."""
        self._cmd_pub.publish(Twist())


def main(args: list | None = None) -> None:
    """Entry point for the simple_waypoint_nav console script."""
    rclpy.init(args=args)
    node = SimpleWaypointNav()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
