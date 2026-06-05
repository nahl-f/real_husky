import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, PointStamped #msg type of goal
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

class HuskyNav(Node):
    def __init__(self):
        super().__init__('husky_nav')
        # navigator
        self.navigator = BasicNavigator(namespace='husky2')
        # storing points
        self.points = {}
        # subscriber for points
        self.subscription = self.create_subscription(PointStamped, '/husky2/clicked_point', self.point_callback, 10)
        self.subscription 
    
    def point_callback(self, msg):
        self.get_logger().info(f"Received point: ({msg.point.x}, {msg.point.y})")
        name = input("Enter a name for this point: ")
        self.points[name] = (msg.point.x, msg.point.y)
        self.get_logger().info(f"Stored location '{name}' at ({msg.point.x}, {msg.point.y})")
        print(self.points)

    def navigate(self):
        self.get_logger().info("Available locations:")
        for name in self.points:
            self.get_logger().info(f"{name}")
        while True:
             name = input("Enter the name of the location [q to quit]): ")
             if name.lower() == 'q':
                self.get_logger().info("Exiting navigation.")
                break
             else:        
                if name in self.points:
                    x, y = self.points[name]
                    goal_pose = PoseStamped()
                    goal_pose.header.frame_id = 'map'
                    goal_pose.pose.position.x = x
                    goal_pose.pose.position.y = y
                    # goal_pose.pose.orientation.w = 0.5

                    self.get_logger().info(f"Navigating to {name}")
                    self.navigator.goToPose(goal_pose)

                    while not self.navigator.isTaskComplete():
                        feedback = self.navigator.getFeedback()
                        if feedback.navigation_time.sec > 120:
                            self.navigator.cancelTask()
                            self.get_logger().info("Navigation taking too long, cancelling task.")
                        if feedback:
                            self.get_logger().info(f"Distance remaining: {feedback.distance_remaining} m")

                    result = self.navigator.getResult()
                    if result == TaskResult.SUCCEEDED:
                        self.get_logger().info(f"Reached '{name}' successfully!")
                    elif result == TaskResult.CANCELED:
                        self.get_logger().warn(f"Navigation to '{name}' was canceled.")
                    elif result == TaskResult.FAILED:
                        self.get_logger().warn(f"Failed to reach '{name}'.")
                else:
                    self.get_logger().warn(f"No location named '{name}' found. Please try again.")
    
def main(args=None):
    rclpy.init(args=args)
    node = HuskyNav()
    while True:
        node.get_logger().info("Click a point to set a location:")
        rclpy.spin_once(node)
        state = input("Enter 'n' to navigate, 'q' to quit, or any enter to continue setting points: ")
        if state.lower() == 'n':
            node.navigate()
        elif state.lower() == 'q':
            break
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()