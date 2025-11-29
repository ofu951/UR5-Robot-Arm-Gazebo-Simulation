#!/usr/bin/env python3
"""
UR5 Robot Arm Cubic Trajectory Test Script
Bu script UR5 robot koluna cubic trajectory gönderir
"""

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import time

class UR5TrajectoryPublisher(Node):
    def __init__(self):
        super().__init__('ur5_trajectory_publisher')
        
        # Joint isimleri
        self.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]
        
        # Publisher oluştur
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/ur/joint_trajectory_controller/joint_trajectory',
            10
        )
        
        # Alternatif: Her joint için ayrı topic (ros_gz_bridge için)
        self.joint_publishers = {}
        from std_msgs.msg import Float64
        for joint_name in self.joint_names:
            self.joint_publishers[joint_name] = self.create_publisher(
                Float64,
                f'/ur/{joint_name}/command',
                10
            )
        
        self.get_logger().info('UR5 Trajectory Publisher başlatıldı')
        self.get_logger().info('ros_gz_bridge için joint command topic\'leri hazır')
        
    def publish_cubic_trajectory(self):
        """Cubic trajectory oluştur ve gönder"""
        
        # Başlangıç pozisyonları (home position)
        start_positions = [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]
        
        # Hedef pozisyonlar (test için)
        end_positions = [0.5, -1.0, 1.0, -0.5, 0.5, 0.3]
        
        # Trajectory parametreleri
        duration = 5.0  # saniye
        num_points = 50
        dt = duration / num_points
        
        self.get_logger().info(f'Cubic trajectory başlatılıyor: {duration} saniye, {num_points} nokta')
        
        # Her nokta için cubic interpolation
        for i in range(num_points + 1):
            t = i / num_points  # 0.0 to 1.0
            
            # Cubic interpolation: s(t) = 3t² - 2t³ (smooth start and end)
            s = 3 * t * t - 2 * t * t * t
            
            # Her joint için pozisyon hesapla
            positions = []
            velocities = []
            
            for j in range(len(self.joint_names)):
                # Position: linear interpolation with cubic easing
                pos = start_positions[j] + s * (end_positions[j] - start_positions[j])
                positions.append(pos)
                
                # Velocity: derivative of cubic easing
                # ds/dt = 6t - 6t²
                ds_dt = 6 * t - 6 * t * t
                vel = ds_dt * (end_positions[j] - start_positions[j]) / duration
                velocities.append(vel)
            
            # JointTrajectory mesajı oluştur
            trajectory = JointTrajectory()
            trajectory.joint_names = self.joint_names
            trajectory.header.stamp = self.get_clock().now().to_msg()
            trajectory.header.frame_id = ''
            
            point = JointTrajectoryPoint()
            point.positions = positions
            point.velocities = velocities
            point.time_from_start.sec = int(i * dt)
            point.time_from_start.nanosec = int((i * dt - int(i * dt)) * 1e9)
            
            trajectory.points = [point]
            
            # Publish
            self.publisher.publish(trajectory)
            
            # Alternatif: ros_gz_bridge için her joint'e ayrı komut gönder
            from std_msgs.msg import Float64
            for j, joint_name in enumerate(self.joint_names):
                msg = Float64()
                msg.data = positions[j]
                self.joint_publishers[joint_name].publish(msg)
            
            self.get_logger().info(f'Point {i}/{num_points}: positions={[f"{p:.2f}" for p in positions]}')
            
            # Bekle
            time.sleep(dt)
        
        self.get_logger().info('Trajectory tamamlandı!')
    
    def publish_simple_movement(self):
        """Basit hareket: Her joint'i sırayla hareket ettir"""
        from std_msgs.msg import Float64
        
        self.get_logger().info('Basit hareket testi başlatılıyor...')
        
        # Her joint için test pozisyonları
        test_positions = [
            [0.5, -1.57, 0.0, -1.57, 0.0, 0.0],  # shoulder_pan
            [0.0, -1.0, 0.0, -1.57, 0.0, 0.0],   # shoulder_lift
            [0.0, -1.57, 1.0, -1.57, 0.0, 0.0],  # elbow
            [0.0, -1.57, 0.0, -0.5, 0.0, 0.0],   # wrist_1
            [0.0, -1.57, 0.0, -1.57, 0.5, 0.0], # wrist_2
            [0.0, -1.57, 0.0, -1.57, 0.0, 0.5], # wrist_3
        ]
        
        for i, (joint_name, positions) in enumerate(zip(self.joint_names, test_positions)):
            self.get_logger().info(f'Hareket ettiriliyor: {joint_name}')
            
            # Her joint'e pozisyon gönder
            for j, pos in enumerate(positions):
                msg = Float64()
                msg.data = pos
                self.joint_publishers[self.joint_names[j]].publish(msg)
            
            time.sleep(2.0)  # 2 saniye bekle
        
        self.get_logger().info('Test tamamlandı!')


def main(args=None):
    rclpy.init(args=args)
    
    node = UR5TrajectoryPublisher()
    
    # 2 saniye bekle (robot spawn olsun)
    time.sleep(2.0)
    
    try:
        # Basit hareket testi (ros_gz_bridge için)
        node.publish_simple_movement()
        
        # 3 saniye bekle
        time.sleep(3.0)
        
        # Cubic trajectory (eğer joint_trajectory_controller varsa)
        # node.publish_cubic_trajectory()
        
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

