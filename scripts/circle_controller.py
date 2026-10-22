#!/usr/bin/env python3
"""
circle_controller.py
功能：读取 rosparam 参数（周期、幅值），控制小乌龟做普通圆周运动
参数可在运行时通过 rosparam set 修改，代码循环读取，立即生效
"""

import rospy
import math
from geometry_msgs.msg import Twist

def main():
    # 初始化节点
    rospy.init_node("circle_controller", anonymous=True)
    
    # 创建发布者：发布速度指令到 /turtle1/cmd_vel
    pub = rospy.Publisher("/turtle1/cmd_vel", Twist, queue_size=10)
    
    # 设置循环频率 50Hz
    rate = rospy.Rate(50)
    
    rospy.loginfo("circle_controller started. Waiting for param changes...")
    
    while not rospy.is_shutdown():
        # ===== 从参数服务器读取参数（每次循环都读，实现运行时热更新）=====
        # 如果参数不存在，用默认值
        period = rospy.get_param("/turtle_period", 6.28)     # 转一圈的秒数
        amplitude = rospy.get_param("/turtle_amplitude", 1.0) # 线速度大小
        
        # ===== 计算速度（普通圆周运动）=====
        twist = Twist()
        
        # 线速度 = 幅值（固定向前）
        twist.linear.x = amplitude
        twist.linear.y = 0.0
        twist.linear.z = 0.0
        
        # 角速度 = 2π / 周期（固定转弯）
        # 周期越大 → 角速度越小 → 圆越大
        if period > 0:
            twist.angular.z = 2 * math.pi / period
        else:
            twist.angular.z = 1.0
        
        twist.angular.x = 0.0
        twist.angular.y = 0.0
        
        # 发布速度指令
        pub.publish(twist)
        
        # 按 50Hz 休眠
        rate.sleep()

if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass