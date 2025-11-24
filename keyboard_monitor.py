import time
from pynput import keyboard
from threading import Thread

class KeyboardMonitor:
    
    def __init__(self):
        # 键盘监听器对象
        self.keyboard_listener = None
        
        # 是否正在监控
        self.is_monitoring = False
        
        # 存储每次按键的时间
        self.key_press_times = []
        
        # 监控开始时间
        self.monitor_start_time = 0
        
        # 上次提醒时间
        self.last_alert_time = 0
        
        # 提醒冷却时间（秒）
        self.alert_cooldown = 10
        
        # 速度提醒回调函数
        self.speed_alert_callback = None
    
    def start_monitoring(self, alert_callback):#开始键盘监控
        # 设置提醒回调函数
        self.speed_alert_callback = alert_callback
        
        # 重置监控数据
        self.is_monitoring = True
        self.key_press_times = []
        self.monitor_start_time = time.time()
        self.last_alert_time = 0
        
        # 启动键盘监听
        self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
        self.keyboard_listener.start()
        
        # 启动速度监控线程
        self.monitor_thread = Thread(target=self._monitor_speed, daemon=True)
        self.monitor_thread.start()
        
        # 调试信息
        print("键盘监控已启动")
    
    def stop_monitoring(self):
        self.is_monitoring = False
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        print("键盘监控已停止")

    def _on_key_press(self, key):#键盘按键事件处理
        # 如果不在监控状态，直接返回
        if not self.is_monitoring:
            return
        
        # 记录按键时间
        current_time = time.time()
        self.key_press_times.append(current_time)
    
    def _monitor_speed(self):#监控打字速度
        print("速度监控线程启动")
        
        while self.is_monitoring:
            current_time = time.time()
            
            # 计算最近5秒内的按键次数
            time_5_seconds_ago = current_time - 5
            recent_keys = [t for t in self.key_press_times if t >= time_5_seconds_ago]
            
            # 计算当前打字速度（字/分钟）
            if len(recent_keys) > 0:
                current_speed = (len(recent_keys) / 5) * 60
            else:
                current_speed = 0
            
            # 只有当有足够数据时才进行速度分析
            if len(self.key_press_times) >= 10:
                total_duration = current_time - self.monitor_start_time
                
                if total_duration > 0:
                    average_speed = (len(self.key_press_times) / total_duration) * 60
                else:
                    average_speed = 0
                
                # 检查速度是否异常
                self._check_speed_alert(current_speed, average_speed, current_time)
            
            # 每秒检查一次
            time.sleep(1)
        
        print("速度监控线程结束")
    
    def _check_speed_alert(self, current_speed, average_speed, current_time):#检查速度是否需要提醒
        # 如果平均速度为0，无法比较
        if average_speed == 0:
            return
        
        # 检查是否在冷却时间内
        if current_time - self.last_alert_time < self.alert_cooldown:
            return
        
        # 计算当前速度与平均速度的比例
        speed_ratio = current_speed / average_speed if average_speed != 0 else 0
        
        # 如果速度变化超过50%，触发提醒
        if speed_ratio > 1.5:  # 速度过快（超过平均速度50%）
            message = f"当前速度: {current_speed:.1f} 字/分钟，平均: {average_speed:.1f} 字/分钟"
            if self.speed_alert_callback:
                self.speed_alert_callback("速度过快", message)
            self.last_alert_time = current_time
            
        elif speed_ratio < 0.5 and current_speed > 0:  # 速度过慢（低于平均速度50%）
            message = f"当前速度: {current_speed:.1f} 字/分钟，平均: {average_speed:.1f} 字/分钟"
            if self.speed_alert_callback:
                self.speed_alert_callback("速度过慢", message)
            self.last_alert_time = current_time
    
    def get_current_speed(self):#获取当前打字速度

        if not self.key_press_times:
            return 0
        
        current_time = time.time()
        time_5_seconds_ago = current_time - 5
        recent_keys = [t for t in self.key_press_times if t >= time_5_seconds_ago]
        
        if len(recent_keys) > 0:
            return (len(recent_keys) / 5) * 60
        else:
            return 0
    
    def get_total_keystrokes(self):#获取总按键次数
        return len(self.key_press_times)
