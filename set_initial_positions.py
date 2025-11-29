#!/usr/bin/env python3
"""
UR5 Robot Arm Initial Position Setter
Robot spawn olduktan sonra initial position'ları set eder
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import time

class UR5InitialPositionSetter(Node):
    def __init__(self):
        super().__init__('ur5_initial_position_setter')
        
        # Joint isimleri
        self.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]
        
        # Initial position'lar (home position)
        self.initial_positions = [
            0.0,      # shoulder_pan_joint
            -1.57,    # shoulder_lift_joint (home position)
            0.0,      # elbow_joint
            -1.57,    # wrist_1_joint (home position)
            0.0,      # wrist_2_joint
            0.0       # wrist_3_joint
        ]
        
        # Publisher'lar oluştur (publishers ismi ROS 2'de rezerve, joint_publishers kullanıyoruz)
        self.joint_publishers = {}
        for joint_name in self.joint_names:
            self.joint_publishers[joint_name] = self.create_publisher(
                Float64,
                f'/ur/{joint_name}/command',
                10
            )
        
        self.get_logger().info('UR5 Initial Position Setter başlatıldı')
        
    def set_initial_positions(self):
        """Initial position'ları set et"""
        self.get_logger().info('Initial position\'lar set ediliyor...')
        
        # Her joint için pozisyon gönder
        for joint_name, position in zip(self.joint_names, self.initial_positions):
            msg = Float64()
            msg.data = position
            self.joint_publishers[joint_name].publish(msg)
            self.get_logger().info(f'{joint_name}: {position:.2f} rad')
        
        # Birkaç kez tekrarla (plugin'lerin yüklenmesi için)
        for i in range(10):
            for joint_name, position in zip(self.joint_names, self.initial_positions):
                msg = Float64()
                msg.data = position
                self.joint_publishers[joint_name].publish(msg)
            time.sleep(0.1)
        
        self.get_logger().info('Initial position\'lar set edildi!')


def main(args=None):
    rclpy.init(args=args)
    
    node = UR5InitialPositionSetter()
    
    # 3 saniye bekle (robot spawn olsun)
    time.sleep(3.0)
    
    try:
        node.set_initial_positions()
        
        # Sürekli position'ları koru
        rate = node.create_rate(10)  # 10 Hz
        while rclpy.ok():
            for joint_name, position in zip(node.joint_names, node.initial_positions):
                msg = Float64()
                msg.data = position
                node.joint_publishers[joint_name].publish(msg)
            rate.sleep()
            
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

