#!/usr/bin/env python3
import rospy
import math
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

# ============ 全局变量 ============
current_x = 0.0
current_y = 0.0
current_theta = 0.0
pose_received = False

def pose_callback(msg):
    """订阅 /turtle1/pose 的回调函数，实时更新乌龟位姿"""
    global current_x, current_y, current_theta, pose_received
    current_x = msg.x
    current_y = msg.y
    current_theta = msg.theta
    pose_received = True

def normalize_angle(angle):
    """将角度归一化到 [-π, π] 之间，避免转圈"""
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle

def main():
    # ============ ROS 节点初始化 ============
    rospy.init_node('line_controller', anonymous=True)
    
    # ============ 发布者和订阅者 ============
    pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
    rospy.Subscriber('/turtle1/pose', Pose, pose_callback)
    
    rate = rospy.Rate(20)  # 20Hz 控制频率
    
    rospy.loginfo("直线跟踪控制器启动，等待位姿数据...")
    while not pose_received and not rospy.is_shutdown():
        rate.sleep()
    
    rospy.loginfo("开始控制：线速度恒定，角速度由反馈控制调节")
    rospy.loginfo("提示：参数已放入循环内，支持 rosparam set 热更新！")
    
    while not rospy.is_shutdown():
        
        # ============ 每次循环都从参数服务器读取（热更新核心） ============
        target_y = rospy.get_param('~target_y', 8.0)
        linear_vel = rospy.get_param('~linear_velocity', 1.0)
        K_y = rospy.get_param('~K_y', 0.8)
        K_theta = rospy.get_param('~K_theta', 2.0)
        
        # ---------- 1. 计算 y 方向误差 ----------
        error_y = target_y - current_y
        
        # ---------- 2. 第一层 P 控制：误差 → 期望朝向 ----------
        desired_vy = K_y * error_y
        sin_theta_d = desired_vy / linear_vel
        sin_theta_d = max(-0.99, min(0.99, sin_theta_d))
        theta_d = math.asin(sin_theta_d)
        
        # ---------- 3. 第二层 P 控制：角度误差 → 角速度 ----------
        error_theta = normalize_angle(theta_d - current_theta)
        angular_vel = K_theta * error_theta
        
        # ---------- 4. 发布速度命令 ----------
        cmd = Twist()
        cmd.linear.x = linear_vel    # 线速度恒定
        cmd.angular.z = angular_vel  # 角速度由反馈控制决定
        pub.publish(cmd)
        
        # ---------- 5. 日志输出 ----------
        if int(rospy.get_time() * 10) % 10 == 0:
            rospy.loginfo_throttle(1.0,
                f"target_y={target_y:.1f} | y={current_y:.2f} | "
                f"error={error_y:.2f} | ω={angular_vel:.2f}")
        
        rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass