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
"""Keyboard/gamepad teleoperation node for the ASPECT rover."""

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class TeleopNode(Node):
    """Publish velocity commands to /cmd_vel from keyboard or gamepad input.

    Topics
    ------
    Publishers:
        /cmd_vel (geometry_msgs/Twist) — velocity commands for the rover

    TODO: Implement keyboard capture (e.g. via pynput) or joy_node bridge.
    """

    LINEAR_SPEED: float = 0.2   # m/s
    ANGULAR_SPEED: float = 0.5  # rad/s

    def __init__(self) -> None:
        """Initialise the teleop node and create publisher."""
        super().__init__('teleop_node')
        self._cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('TeleopNode started — publish to /cmd_vel')

    def send_velocity(self, linear: float, angular: float) -> None:
        """Publish a single Twist message.

        Parameters
        ----------
        linear:
            Forward/backward velocity in m/s.
        angular:
            Rotational velocity in rad/s.
        """
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        self._cmd_pub.publish(msg)

    def stop(self) -> None:
        """Publish a zero-velocity command to halt the rover."""
        self.send_velocity(0.0, 0.0)
        self.get_logger().info('Stopping rover')


def main(args: list | None = None) -> None:
    """Entry point for the teleop_node console script."""
    rclpy.init(args=args)
    node = TeleopNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.stop()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
