#!/usr/bin/env python3
"""
Controller'ı başlatmak için yardımcı script
"""

import rclpy
from rclpy.node import Node
from controller_manager_msgs.srv import SwitchController, ListControllers
import sys


class ControllerStarter(Node):
    def __init__(self):
        super().__init__('controller_starter')
        
        self.switch_client = self.create_client(
            SwitchController,
            '/controller_manager/switch_controllers'
        )
        
        self.list_client = self.create_client(
            ListControllers,
            '/controller_manager/list_controllers'
        )
        
    def list_controllers(self):
        """Mevcut controller'ları listele"""
        if not self.list_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('List controllers service bulunamadı!')
            return None
        
        request = ListControllers.Request()
        future = self.list_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result():
            return future.result()
        return None
    
    def start_controller(self, controller_name):
        """Controller'ı başlat"""
        if not self.switch_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('Switch controllers service bulunamadı!')
            return False
        
        request = SwitchController.Request()
        request.activate_controllers = [controller_name]
        request.strictness = SwitchController.Request.BEST_EFFORT
        
        future = self.switch_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result():
            result = future.result()
            if result.ok:
                self.get_logger().info(f'✓ Controller başlatıldı: {controller_name}')
                return True
            else:
                self.get_logger().error(f'✗ Controller başlatılamadı: {result.ok}')
                return False
        return False


def main():
    rclpy.init()
    
    starter = ControllerStarter()
    
    # Controller'ları listele
    starter.get_logger().info('Mevcut controller\'lar:')
    result = starter.list_controllers()
    if result:
        for controller in result.controller:
            state = "aktif" if controller.state == "active" else "inaktif"
            starter.get_logger().info(f'  - {controller.name}: {state}')
    
    # Joint trajectory controller'ı başlat
    starter.get_logger().info('')
    starter.get_logger().info('joint_trajectory_controller başlatılıyor...')
    success = starter.start_controller('joint_trajectory_controller')
    
    if success:
        starter.get_logger().info('')
        starter.get_logger().info('✓ Controller başarıyla başlatıldı!')
        starter.get_logger().info('Artık move_ur5.py scriptini çalıştırabilirsiniz.')
    else:
        starter.get_logger().error('')
        starter.get_logger().error('✗ Controller başlatılamadı!')
    
    starter.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

