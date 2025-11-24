#  iFish - 智能打字演示器

所需要的包：

```
ttkbootstrap
tk
pynput
python-dateutil
```

运行：

```
python main.py
```

## 后端类 —— keyboard_monitor

### 设置状态：

```python
 def __init__(self):
        self.keyboard_listener = None # 键盘监听器对象
        self.is_monitoring = False # 是否正在监控
        self.key_press_times = []# 存储每次按键的时间
        self.monitor_start_time = 0# 监控开始时间
        self.last_alert_time = 0# 上次提醒时间
        self.alert_cooldown = 10# 提醒冷却时间（秒）
        self.speed_alert_callback = None# 速度提醒回调函数
```



### 开始键盘监控：

```python
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
```

- 回调函数设置

```python
self.speed_alert_callback = alert_callback
```

- 启动速度监控线程

```python
        self.monitor_thread = Thread(target=self._monitor_speed, daemon=True)
        self.monitor_thread.start()

```

Thread = 创建一个线程。

- **`target=self._monitor_speed`**：指定线程要执行的函数
- **`daemon=True`**：设置为守护线程



### 监控打字速度：

```python
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
```



```python
while self.is_monitoring:
```

- **循环条件**：`self.is_monitoring` 为 `True` 时持续运行
- **退出条件**：当用户停止测试或程序退出时，将此标志设为 `False`
- **作用**：创建一个持续运行的监控环境

```python
current_time = time.time()
```

`time.time()` 就是获取一个精确的时间"坐标"，用于测量时间间隔、计算速度、控制频率等时间相关的操作。

```python
time.sleep(1)
```

- 每秒检查一次



### 检查速度是否需要提醒：

```python
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
```

- 速度的评判标准是，平均速度的50%



### 获取当前打字速度：

```python
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
```



```python
        if not self.key_press_times:
            return 0
```

- 检查 `self.key_press_times` 列表是否为空
- 如果没有任何按键记录，直接返回速度 0
- **防止错误**：避免对空列表进行操作



```python
if len(recent_keys) > 0:
    return (len(recent_keys) / 5) * 60
else:
    return 0
```

- 当前速度 = (最近5秒按键次数 ÷ 5秒) × 60秒/分钟



### 获取总按键次数:

```python
def get_total_keystrokes(self):#获取总按键次数
        return len(self.key_press_times)
```

- 从key_press_times中获取总按键次数



## 后端类——data_manager

### 管理数据的类

```python
def __init__(self, data_file_name="typing_data.json"):# 初始化数据管理器

        # 保存数据的文件路径
        self.data_file_path = data_file_name
        
        # 存储所有历史测试数据的列表
        self.all_test_data = []
        
        # 程序启动时自动加载历史数据
        self.load_data()
```

初始化数据管理器

### 从文件加载历史数据:

```python
def load_data(self):#从文件加载历史数据

        # 检查数据文件是否存在
        if not os.path.exists(self.data_file_path):
            print("数据文件不存在，创建新的数据文件")
            return
        
        try:
            # 打开文件并读取数据
            with open(self.data_file_path, 'r', encoding='utf-8') as file:
                loaded_data = json.load(file)
                self.all_test_data = loaded_data
                print(f"成功加载 {len(self.all_test_data)} 条历史记录")
                
        except Exception as error:
            print(f"加载数据时出错: {error}")
            self.all_test_data = []
```

#### 从文件加载历史数据:

```python
if not os.path.exists(self.data_file_path):
    print("数据文件不存在，创建新的数据文件")
    return
```

- 使用 `os.path.exists()` 检查数据文件是否存在
- **文件不存在**：输出提示信息并直接返回
- **文件存在**：继续执行加载操作



#### **文件打开部分**：

```python
with open(self.data_file_path, 'r', encoding='utf-8') as file:
```

- **`'r'`**：以只读模式打开文件
- **`encoding='utf-8'`**：指定UTF-8编码，支持中文
- **`with` 语句**：自动管理文件资源，确保文件正确关闭



### 保存一次测试的结果：

```python
 def save_test(self, test_data):#保存一次测试的结果
        # 将新数据添加到历史数据中
        self.all_test_data.append(test_data)
        
        # 保存到文件
        try:
            with open(self.data_file_path, 'w', encoding='utf-8') as file:
                json.dump(self.all_test_data, file, ensure_ascii=False, indent=2)
            print("测试结果保存成功")
            
        except Exception as error:
            print(f"保存数据时出错: {error}")
```

- **`'w'`**：以写入模式打开文件
  - 如果文件不存在，会自动创建
  - 如果文件已存在，会清空原有内容后重新写入
- **`encoding='utf-8'`**：指定UTF-8编码，确保中文正确保存
- **`with` 语句**：自动管理文件资源，确保文件正确关闭



```python
json.dump(self.all_test_data, file, ensure_ascii=False, indent=2)
```

- **`self.all_test_data`**：要保存的Python数据（列表）
- **`file`**：文件对象，数据将写入这个文件
- **`ensure_ascii=False`**：允许非ASCII字符（如中文）直接保存，而不是转义为Unicode编码
- **`indent=2`**：设置缩进为2个空格，使JSON文件易于阅读



### 获取最近的测试记录：

```python
def get_recent_tests(self, count=5):# 获取最近的测试记录

        # 如果历史数据为空，返回空列表
        if not self.all_test_data:
            return []
        
        # 获取最后count条记录，并反转顺序（最新的在前面）
        recent_tests = list(reversed(self.all_test_data[-count:]))
        return recent_tests
    
```



#### 切片获取最后count条记录

```python
self.all_test_data[-count:]
```

- ##### -count：使用负数索引进行切片

- **含义**：从列表末尾开始，取最后count个元素
- **示例**：如果 `count=5`，则取列表的最后5个元素

#### 反转顺序

```python
reversed(self.all_test_data[-count:])
```

- **`reversed()`**：返回一个反转的迭代器
- **效果**：将顺序从"旧→新"变为"新→旧"

#### **转换为列表**

```python
list(reversed(...))
```

- **`list()`**：将反转的迭代器转换为实际的列表
- **必要步骤**：因为 `reversed()` 返回的是迭代器，不是列表



### 清除所有历史数据：

```python
def clear_all_data(self):#清除所有历史数据

        # 清空内存中的数据
        self.all_test_data = []
        
        # 清空文件中的数据
        try:
            with open(self.data_file_path, 'w', encoding='utf-8') as file:
                json.dump([], file)
            print("历史数据清除成功")
            
        except Exception as error:
            print(f"清除数据时出错: {error}")
```

#### **文件打开部分**：

```python
with open(self.data_file_path, 'w', encoding='utf-8') as file:
```

- **`'w'`**：以写入模式打开文件
  - 如果文件不存在，会创建新文件
  - 如果文件已存在，会**清空所有内容**后重新写入
- **`encoding='utf-8'`**：指定UTF-8编码
- **`with` 语句**：自动管理文件资源

#### **写入空数据**：

```python
json.dump([], file)
```

- **`[]`**：写入一个空的Python列表
- **效果**：JSON文件内容变为 `[]`（空数组）
- **目的**：确保文件格式仍然是有效的JSON