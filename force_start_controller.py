#!/usr/bin/env python3
"""
Controller'ı zorla başlatmak için script
Service bulunamazsa spawner kullanır
"""

import rclpy
from rclpy.node import Node
from controller_manager_msgs.srv import SwitchController, ListControllers
import subprocess
import time
import sys


class ForceControllerStarter(Node):
    def __init__(self):
        super().__init__('force_controller_starter')
        
        # Service client'ları oluştur
        self.switch_client = self.create_client(
            SwitchController,
            '/controller_manager/switch_controllers'
        )
        
        self.list_client = self.create_client(
            ListControllers,
            '/controller_manager/list_controllers'
        )
        
    def wait_and_list_controllers(self, timeout=10.0):
        """Controller listesini al"""
        self.get_logger().info('Controller listesi alınıyor...')
        
        # Service'in hazır olmasını bekle
        if not self.list_client.wait_for_service(timeout_sec=timeout):
            self.get_logger().warn('List controllers service bulunamadı, spawner kullanılacak')
            return None
        
        request = ListControllers.Request()
        future = self.list_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
        
        if future.done() and future.result():
            return future.result()
        return None
    
    def start_via_service(self, controller_name):
        """Service ile controller başlat"""
        if not self.switch_client.wait_for_service(timeout_sec=5.0):
            return False
        
        request = SwitchController.Request()
        request.activate_controllers = [controller_name]
        request.strictness = SwitchController.Request.BEST_EFFORT
        
        future = self.switch_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        
        if future.done() and future.result():
            result = future.result()
            if result.ok:
                self.get_logger().info(f'✓ Service ile controller başlatıldı: {controller_name}')
                return True
        return False
    
    def start_via_spawner(self, controller_name):
        """Spawner ile controller başlat"""
        self.get_logger().info(f'Spawner ile {controller_name} başlatılıyor...')
        
        try:
            # Spawner'ı çalıştır
            result = subprocess.run(
                ['ros2', 'run', 'controller_manager', 'spawner',
                 controller_name, '--controller-manager', '/controller_manager'],
                capture_output=True,
                text=True,
                timeout=15.0
            )
            
            if result.returncode == 0:
                self.get_logger().info(f'✓ Spawner ile controller başlatıldı: {controller_name}')
                return True
            else:
                self.get_logger().warn(f'Spawner çıktısı: {result.stderr}')
                return False
        except subprocess.TimeoutExpired:
            self.get_logger().error('Spawner timeout!')
            return False
        except Exception as e:
            self.get_logger().error(f'Spawner hatası: {e}')
            return False


def main():
    rclpy.init()
    
    starter = ForceControllerStarter()
    
    # Önce controller listesini al
    result = starter.wait_and_list_controllers(timeout=10.0)
    
    if result:
        starter.get_logger().info('Mevcut controller\'lar:')
        for controller in result.controller:
            state = controller.state
            starter.get_logger().info(f'  - {controller.name}: {state}')
            
            # Eğer joint_trajectory_controller varsa ve inactive ise
            if controller.name == 'joint_trajectory_controller' and state != 'active':
                starter.get_logger().info(f'  → {controller.name} aktif değil, başlatılıyor...')
                
                # Önce service ile dene
                if not starter.start_via_service('joint_trajectory_controller'):
                    # Service çalışmazsa spawner kullan
                    starter.get_logger().info('Service çalışmadı, spawner deneniyor...')
                    starter.start_via_spawner('joint_trajectory_controller')
    else:
        starter.get_logger().warn('Controller listesi alınamadı, spawner ile başlatılıyor...')
        starter.start_via_spawner('joint_trajectory_controller')
    
    # Biraz bekle ve action server'ı kontrol et
    starter.get_logger().info('')
    starter.get_logger().info('Action server kontrol ediliyor...')
    time.sleep(3)
    
    try:
        result = subprocess.run(
            ['ros2', 'action', 'list'],
            capture_output=True,
            text=True,
            timeout=5.0
        )
        if 'trajectory' in result.stdout:
            starter.get_logger().info('✓ Action server bulundu!')
            for line in result.stdout.split('\n'):
                if 'trajectory' in line:
                    starter.get_logger().info(f'  - {line.strip()}')
        else:
            starter.get_logger().warn('Action server henüz görünmüyor, birkaç saniye daha bekleyin...')
    except Exception as e:
        starter.get_logger().warn(f'Action listesi alınamadı: {e}')
    
    starter.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

