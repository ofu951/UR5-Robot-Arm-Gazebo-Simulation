#!/usr/bin/env python3
"""
UR5 Robot için Cubic Trajectory ile Hareket Scripti
Belirli bir noktaya veya joint açılarına robot kolunu cubic interpolation ile hareket ettirir
"""

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient
from sensor_msgs.msg import JointState
import time
import math
import sys


class UR5TrajectoryController(Node):
    def __init__(self):
        super().__init__('ur5_trajectory_controller')
        
        # Joint isimleri (UR5 için)
        self.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]
        
        # Mevcut joint pozisyonları
        self.current_positions = [0.0] * len(self.joint_names)
        self.joint_state_received = False
        
        # Joint state subscriber - QoS ayarları ile
        from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            qos_profile
        )
        
        # Action client oluştur - farklı namespace'leri dene
        self.action_clients = []
        possible_namespaces = [
            '/joint_trajectory_controller/follow_joint_trajectory',
            '/controller_manager/joint_trajectory_controller/follow_joint_trajectory',
            '/ur/joint_trajectory_controller/follow_joint_trajectory',
        ]
        
        for namespace in possible_namespaces:
            client = ActionClient(self, FollowJointTrajectory, namespace)
            self.action_clients.append((namespace, client))
        
        self.active_client = None
        self.get_logger().info('UR5 Trajectory Controller başlatıldı...')
        
    def joint_state_callback(self, msg):
        """Joint state'den mevcut pozisyonları al"""
        if not self.joint_state_received:
            self.joint_state_received = True
        
        # Joint isimlerine göre pozisyonları eşleştir
        for i, joint_name in enumerate(self.joint_names):
            try:
                idx = msg.name.index(joint_name)
                self.current_positions[i] = msg.position[idx]
            except (ValueError, IndexError):
                pass
    
    def wait_for_joint_state(self, timeout=5.0):
        """Joint state mesajını bekle"""
        start_time = time.time()
        while not self.joint_state_received and (time.time() - start_time) < timeout:
            rclpy.spin_once(self, timeout_sec=0.2)
        if self.joint_state_received:
            self.get_logger().info(f'Joint state alındı: {[f"{p:.3f}" for p in self.current_positions]}')
        return self.joint_state_received
    
    def wait_for_server(self, timeout_sec=15.0):
        """Action server'ın hazır olmasını bekle - tüm olası namespace'leri dene"""
        self.get_logger().info('Action server aranıyor...')
        
        # Önce mevcut action server'ları listele
        self.list_available_actions()
        
        # Her namespace için daha uzun timeout dene
        for namespace, client in self.action_clients:
            self.get_logger().info(f'  Deneniyor: {namespace}')
            # Biraz bekle ve tekrar dene
            time.sleep(0.5)
            if client.wait_for_server(timeout_sec=5.0):
                self.active_client = client
                self.get_logger().info(f'✓ Action server bulundu: {namespace}')
                return True
            else:
                self.get_logger().warn(f'  Timeout: {namespace}')
        
        # Eğer bulunamadıysa, action server'ları tekrar listele
        self.get_logger().error('✗ Hiçbir action server bulunamadı!')
        self.get_logger().info('Mevcut action server\'ları tekrar kontrol ediliyor...')
        self.list_available_actions()
        
        # Son bir deneme - direkt action info ile kontrol et
        self.get_logger().info('Son deneme: Action server durumu kontrol ediliyor...')
        return self.try_direct_connection()
    
    def try_direct_connection(self):
        """Direkt olarak action server'a bağlanmayı dene"""
        import subprocess
        for namespace, client in self.action_clients:
            try:
                # Action info ile kontrol et
                result = subprocess.run(
                    ['ros2', 'action', 'info', namespace],
                    capture_output=True,
                    text=True,
                    timeout=3.0
                )
                if result.returncode == 0 and 'Action clients' in result.stdout:
                    # Server var, tekrar bekle
                    self.get_logger().info(f'Server mevcut, tekrar bekleniyor: {namespace}')
                    if client.wait_for_server(timeout_sec=10.0):
                        self.active_client = client
                        self.get_logger().info(f'✓ Action server bağlantısı başarılı: {namespace}')
                        return True
            except Exception as e:
                continue
        return False
    
    def list_available_actions(self):
        """Mevcut action server'ları listele"""
        try:
            import subprocess
            result = subprocess.run(
                ['ros2', 'action', 'list'],
                capture_output=True,
                text=True,
                timeout=3.0
            )
            if result.returncode == 0:
                self.get_logger().info('Mevcut action server\'lar:')
                actions = result.stdout.strip().split('\n')
                if actions and actions[0]:
                    for line in actions:
                        if line.strip():
                            self.get_logger().info(f'  - {line.strip()}')
                else:
                    self.get_logger().warn('  (Hiç action server bulunamadı)')
        except Exception as e:
            self.get_logger().warn(f'Action listesi alınamadı: {e}')
    
    def cubic_interpolation(self, start, end, t):
        """
        Cubic interpolation: p(t) = start + (end - start) * (3t² - 2t³)
        t: 0.0 ile 1.0 arasında
        """
        t = max(0.0, min(1.0, t))  # Clamp to [0, 1]
        # Cubic ease-in-out: 3t² - 2t³
        factor = 3 * t * t - 2 * t * t * t
        return [s + (e - s) * factor for s, e in zip(start, end)]
    
    def create_cubic_trajectory(self, start_positions, end_positions, duration=5.0, num_points=50):
        """
        Cubic interpolation kullanarak trajectory oluştur
        
        Args:
            start_positions: Başlangıç joint pozisyonları (radyan)
            end_positions: Hedef joint pozisyonları (radyan)
            duration: Hareket süresi (saniye)
            num_points: Trajectory'deki nokta sayısı
        """
        trajectory = JointTrajectory()
        trajectory.joint_names = self.joint_names
        
        # Time step hesapla
        dt = duration / num_points
        
        for i in range(num_points + 1):
            t = i / num_points  # 0.0 to 1.0
            
            # Cubic interpolation ile pozisyon hesapla
            positions = self.cubic_interpolation(start_positions, end_positions, t)
            
            # Velocity hesapla (cubic'in türevi)
            if i == 0:
                velocities = [0.0] * len(self.joint_names)
            elif i == num_points:
                velocities = [0.0] * len(self.joint_names)
            else:
                # Cubic'in türevi: 6t - 6t²
                t_prev = (i - 1) / num_points
                t_next = (i + 1) / num_points
                factor_prev = 6 * t_prev - 6 * t_prev * t_prev
                factor_next = 6 * t_next - 6 * t_next * t_next
                velocities = [
                    (end - start) * (factor_next - factor_prev) / (2 * dt)
                    for start, end in zip(start_positions, end_positions)
                ]
            
            # Trajectory point oluştur
            point = JointTrajectoryPoint()
            point.positions = positions
            point.velocities = velocities
            point.time_from_start.sec = int(i * dt)
            point.time_from_start.nanosec = int((i * dt - int(i * dt)) * 1e9)
            
            trajectory.points.append(point)
        
        return trajectory
    
    def inverse_kinematics_approx(self, x, y, z):
        """
        Basitleştirilmiş inverse kinematics
        Belirli bir noktaya ulaşmak için joint açılarını hesapla
        """
        # UR5 robot parametreleri (metre cinsinden)
        d1 = 0.089159
        a2 = -0.425
        a3 = -0.39225
        
        # Basit geometrik yaklaşım
        # shoulder_pan: x-y düzleminde açı
        theta1 = math.atan2(y, x)
        
        # Mesafe hesapla
        r = math.sqrt(x*x + y*y)
        # Z yüksekliği (base'den)
        z_eff = z - d1
        
        # Basit 2D inverse kinematics
        L1 = abs(a2)  # 0.425
        L2 = abs(a3)  # 0.39225
        
        # Hedef mesafe
        d = math.sqrt(r*r + z_eff*z_eff)
        
        # Cosine law ile açıları hesapla
        if d > (L1 + L2) or d < abs(L1 - L2):
            self.get_logger().warn(f'Hedef nokta ulaşılabilir alan dışında! d={d:.3f}, limit: {L1+L2:.3f}')
            d = min(d, L1 + L2 - 0.1)  # Limit içinde tut
        
        cos_elbow = (L1*L1 + L2*L2 - d*d) / (2*L1*L2)
        cos_elbow = max(-1.0, min(1.0, cos_elbow))  # Clamp
        theta3 = math.acos(cos_elbow) - math.pi  # UR5 için
        
        # Shoulder lift açısı
        alpha = math.atan2(z_eff, r)
        beta = math.acos((L1*L1 + d*d - L2*L2) / (2*L1*d))
        theta2 = alpha - beta - math.pi/2  # UR5 için
        
        # Wrist açıları (basit yaklaşım - end effector'i düz tut)
        theta4 = -theta2 - theta3
        theta5 = 0.0
        theta6 = 0.0
        
        return [theta1, theta2, theta3, theta4, theta5, theta6]
    
    def move_to_position(self, target_positions, duration=5.0, use_current=True):
        """
        Robotu belirli bir pozisyona cubic trajectory ile hareket ettir
        
        Args:
            target_positions: Hedef joint pozisyonları (radyan listesi)
            duration: Hareket süresi (saniye)
            use_current: Mevcut pozisyonu başlangıç olarak kullan
        """
        if len(target_positions) != len(self.joint_names):
            self.get_logger().error(f'Pozisyon sayısı ({len(target_positions)}) joint sayısına ({len(self.joint_names)}) eşit değil!')
            return False
        
        # Başlangıç pozisyonları
        if use_current and self.joint_state_received:
            start_positions = self.current_positions.copy()
            self.get_logger().info(f'Başlangıç pozisyonları (mevcut): {[f"{p:.3f}" for p in start_positions]}')
        else:
            start_positions = [0.0] * len(self.joint_names)
            self.get_logger().info(f'Başlangıç pozisyonları (sıfır): {[f"{p:.3f}" for p in start_positions]}')
        
        self.get_logger().info(f'Hedef pozisyonlar: {[f"{p:.3f}" for p in target_positions]}')
        
        # Cubic trajectory oluştur
        trajectory = self.create_cubic_trajectory(start_positions, target_positions, duration)
        
        # Action goal oluştur
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = trajectory
        
        # Goal gönder
        self.get_logger().info('Trajectory gönderiliyor...')
        send_goal_future = self.active_client.send_goal_async(goal_msg)
        
        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle = send_goal_future.result()
        
        if not goal_handle.accepted:
            self.get_logger().error('Goal kabul edilmedi!')
            return False
        
        self.get_logger().info('Goal kabul edildi, hareket başladı...')
        
        # Sonucu bekle
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        
        result = result_future.result().result
        if result.error_code == FollowJointTrajectory.Result.SUCCESSFUL:
            self.get_logger().info('✓ Hareket başarıyla tamamlandı!')
            return True
        else:
            self.get_logger().error(f'✗ Hareket başarısız! Error code: {result.error_code}')
            return False
    
    def move_to_point(self, x, y, z, duration=6.0):
        """
        Robotu belirli bir 3D noktaya hareket ettir
        
        Args:
            x, y, z: Hedef nokta koordinatları (metre, base frame'de)
            duration: Hareket süresi (saniye)
        """
        self.get_logger().info(f'Hedef nokta: x={x:.3f}m, y={y:.3f}m, z={z:.3f}m')
        
        # Inverse kinematics ile joint açılarını hesapla
        target_joints = self.inverse_kinematics_approx(x, y, z)
        
        self.get_logger().info(f'Hesaplanan joint açıları (rad): {[f"{j:.3f}" for j in target_joints]}')
        self.get_logger().info(f'Hesaplanan joint açıları (deg): {[f"{math.degrees(j):.1f}" for j in target_joints]}')
        
        # Hareketi başlat
        return self.move_to_position(target_joints, duration, use_current=True)


def main():
    rclpy.init()
    
    controller = UR5TrajectoryController()
    
    # Joint state'i bekle
    controller.get_logger().info('Joint state bekleniyor...')
    if not controller.wait_for_joint_state(timeout=3.0):
        controller.get_logger().warn('Joint state alınamadı, sıfırdan başlanacak')
    
    # Action server'ı bekle
    if not controller.wait_for_server():
        controller.get_logger().error('Action server bulunamadı!')
        controller.get_logger().info('')
        controller.get_logger().info('Lütfen şunları kontrol edin:')
        controller.get_logger().info('1. Gazebo simülasyonunun çalıştığından emin olun')
        controller.get_logger().info('2. Controller\'ı başlatın: python3 start_controller.py')
        controller.get_logger().info('   veya: ros2 service call /controller_manager/switch_controllers controller_manager_msgs/srv/SwitchController "{activate_controllers: [joint_trajectory_controller]}"')
        controller.destroy_node()
        rclpy.shutdown()
        return
    
    controller.get_logger().info('')
    controller.get_logger().info('=' * 60)
    controller.get_logger().info('UR5 Robot Cubic Trajectory Hareketi')
    controller.get_logger().info('=' * 60)
    controller.get_logger().info('')
    
    # Kullanım modu seç
    if len(sys.argv) > 1 and sys.argv[1] == '--point':
        # 3D nokta modu
        if len(sys.argv) >= 5:
            x, y, z = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
            duration = float(sys.argv[5]) if len(sys.argv) > 5 else 6.0
        else:
            # Varsayılan nokta
            x, y, z = 0.4, 0.2, 0.3
            duration = 6.0
        
        controller.get_logger().info(f'Mod: 3D Noktaya Hareket')
        controller.get_logger().info(f'Hedef: x={x:.3f}m, y={y:.3f}m, z={z:.3f}m')
        success = controller.move_to_point(x, y, z, duration)
    else:
        # Joint açıları modu
        if len(sys.argv) > 1:
            # Komut satırından joint açıları
            target_positions = [float(x) for x in sys.argv[1:7]]
            duration = float(sys.argv[7]) if len(sys.argv) > 7 else 6.0
        else:
            # Varsayılan pozisyonlar
            target_positions = [
                0.5,   # shoulder_pan_joint: sağa dön
                -1.0,  # shoulder_lift_joint: yukarı kaldır
                1.5,   # elbow_joint: dirsek bük
                -1.0,  # wrist_1_joint
                1.5,   # wrist_2_joint
                0.0    # wrist_3_joint
            ]
            duration = 6.0
        
        controller.get_logger().info(f'Mod: Joint Açılarına Hareket')
        controller.get_logger().info(f'Hedef açılar (rad): {[f"{p:.3f}" for p in target_positions]}')
        success = controller.move_to_position(target_positions, duration)
    
    controller.get_logger().info('')
    if success:
        controller.get_logger().info('=' * 60)
        controller.get_logger().info('✓ Hareket başarıyla tamamlandı!')
        controller.get_logger().info('=' * 60)
    else:
        controller.get_logger().info('=' * 60)
        controller.get_logger().info('✗ Hareket sırasında hata oluştu!')
        controller.get_logger().info('=' * 60)
    
    controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

