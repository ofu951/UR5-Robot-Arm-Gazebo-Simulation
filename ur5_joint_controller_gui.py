#!/usr/bin/env python3
"""
UR5 Robot Arm Joint Controller GUI
Tkinter ile trackbar/slider kullanarak joint'leri kontrol eder
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import tkinter as tk
from tkinter import ttk
import threading
import time

class UR5JointControllerGUI(Node):
    def __init__(self):
        super().__init__('ur5_joint_controller_gui')
        
        # Joint isimleri ve limitleri (radyan)
        self.joint_configs = [
            {
                'name': 'shoulder_pan_joint',
                'min': -3.14,
                'max': 3.14,
                'default': 0.0,
                'label': 'Shoulder Pan'
            },
            {
                'name': 'shoulder_lift_joint',
                'min': -3.14,
                'max': 3.14,
                'default': -1.57,
                'label': 'Shoulder Lift'
            },
            {
                'name': 'elbow_joint',
                'min': -3.14,
                'max': 3.14,
                'default': 0.0,
                'label': 'Elbow'
            },
            {
                'name': 'wrist_1_joint',
                'min': -3.14,
                'max': 3.14,
                'default': -1.57,
                'label': 'Wrist 1'
            },
            {
                'name': 'wrist_2_joint',
                'min': -3.14,
                'max': 3.14,
                'default': 0.0,
                'label': 'Wrist 2'
            },
            {
                'name': 'wrist_3_joint',
                'min': -3.14,
                'max': 3.14,
                'default': 0.0,
                'label': 'Wrist 3'
            },
        ]
        
        # Publisher'lar oluştur
        self.joint_publishers = {}
        self.current_positions = {}
        
        for joint_config in self.joint_configs:
            joint_name = joint_config['name']
            self.joint_publishers[joint_name] = self.create_publisher(
                Float64,
                f'/ur/{joint_name}/command',
                10
            )
            self.current_positions[joint_name] = joint_config['default']
        
        self.get_logger().info('UR5 Joint Controller GUI başlatıldı')
        
        # GUI oluştur
        self.create_gui()
        
        # ROS spin thread'i başlat
        self.spin_thread = threading.Thread(target=self.spin_node, daemon=True)
        self.spin_thread.start()
        
    def create_gui(self):
        """Tkinter GUI oluştur"""
        self.root = tk.Tk()
        self.root.title("UR5 Joint Controller")
        self.root.geometry("500x600")
        
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Başlık
        title_label = ttk.Label(main_frame, text="UR5 Robot Arm Joint Controller", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Her joint için slider
        self.sliders = {}
        self.value_labels = {}
        
        for i, joint_config in enumerate(self.joint_configs):
            row = i + 1
            
            # Joint adı
            label = ttk.Label(main_frame, text=joint_config['label'] + ":", 
                             font=("Arial", 10))
            label.grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
            
            # Değer label'ı
            value_label = ttk.Label(main_frame, text=f"{joint_config['default']:.2f} rad",
                                   width=10, font=("Arial", 9))
            value_label.grid(row=row, column=1, sticky=tk.E, padx=5)
            self.value_labels[joint_config['name']] = value_label
            
            # Slider
            slider = ttk.Scale(
                main_frame,
                from_=joint_config['min'],
                to=joint_config['max'],
                value=joint_config['default'],
                orient=tk.HORIZONTAL,
                length=300,
                command=lambda val, name=joint_config['name']: self.on_slider_change(name, val)
            )
            slider.grid(row=row, column=2, sticky=(tk.W, tk.E), padx=5)
            self.sliders[joint_config['name']] = slider
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(self.joint_configs) + 1, column=0, columnspan=3, pady=20)
        
        # Home position butonu
        home_button = ttk.Button(button_frame, text="Home Position", 
                                command=self.set_home_position)
        home_button.grid(row=0, column=0, padx=5)
        
        # Reset butonu
        reset_button = ttk.Button(button_frame, text="Reset (All Zero)", 
                                 command=self.reset_all)
        reset_button.grid(row=0, column=1, padx=5)
        
        # Grid weight ayarları
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(2, weight=1)
        
        # Kapatma event'i
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_slider_change(self, joint_name, value):
        """Slider değiştiğinde çağrılır"""
        try:
            position = float(value)
            self.current_positions[joint_name] = position
            
            # Değer label'ını güncelle
            self.value_labels[joint_name].config(text=f"{position:.2f} rad")
            
            # ROS topic'e gönder
            msg = Float64()
            msg.data = position
            self.joint_publishers[joint_name].publish(msg)
            
            self.get_logger().info(f'{joint_name}: {position:.2f} rad')
        except ValueError:
            pass
    
    def set_home_position(self):
        """Home position'a getir"""
        for joint_config in self.joint_configs:
            joint_name = joint_config['name']
            default = joint_config['default']
            self.sliders[joint_name].set(default)
            self.current_positions[joint_name] = default
            self.value_labels[joint_name].config(text=f"{default:.2f} rad")
            
            msg = Float64()
            msg.data = default
            self.joint_publishers[joint_name].publish(msg)
        
        self.get_logger().info('Home position set edildi')
    
    def reset_all(self):
        """Tüm joint'leri 0'a getir"""
        for joint_config in self.joint_configs:
            joint_name = joint_config['name']
            self.sliders[joint_name].set(0.0)
            self.current_positions[joint_name] = 0.0
            self.value_labels[joint_name].config(text="0.00 rad")
            
            msg = Float64()
            msg.data = 0.0
            self.joint_publishers[joint_name].publish(msg)
        
        self.get_logger().info('Tüm joint\'ler reset edildi')
    
    def spin_node(self):
        """ROS node'u spin et (ayrı thread'de)"""
        rclpy.spin(self)
    
    def on_closing(self):
        """Pencere kapatıldığında"""
        self.root.destroy()
        rclpy.shutdown()
    
    def run(self):
        """GUI'yi çalıştır"""
        self.root.mainloop()


def main(args=None):
    rclpy.init(args=args)
    
    node = UR5JointControllerGUI()
    
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

