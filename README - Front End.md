# iFish - 智能打字演示器

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



## 前端类 —— ui.py

#### **`__init__` - 初始化方法：**

```python
    def __init__(self, root):
        self.root = root
        self.root.title("TypeFlow - 智能打字演示器")
        self.root.geometry("1200x800")
        self.style = ttk.Style("cosmo")

        # 核心对象
        self.typewriter = TypeWriter() # 调用typewriter包
        self.keyboard_monitor = KeyboardMonitor() # 调用keyboard_monitor包
        self.data_manager = DataManager() # 调用data_manager包

        # 统计相关
        self.started = False
        self.start_time = None
        self.end_time = None
        self.typed_chars = 0
        self.key_events = 0
        self.stopped = False

        # 顶部工具栏
        top_frame = ttk.Frame(root)
        top_frame.pack(fill=X, padx=10, pady=6)

        ttk.Button(top_frame, text="打开文件", command=self.load_text, bootstyle=PRIMARY).pack(side=LEFT, padx=6)
        ttk.Button(top_frame, text="聚焦并开始 (按键触发显示)", command=self.focus_textbox, bootstyle=SUCCESS).pack(side=LEFT, padx=6)
        ttk.Button(top_frame, text="停止并统计", command=self.stop_and_show_stats, bootstyle=DANGER).pack(side=LEFT, padx=6)
        ttk.Button(top_frame, text="重置", command=self.reset, bootstyle=INFO).pack(side=LEFT, padx=6)
        ttk.Button(top_frame, text="数据分析 / 历史", command=self.show_data_dashboard, bootstyle=SECONDARY).pack(side=LEFT, padx=6)

        # 文本显示区
        self.text_box = tk.Text(root, font=("Consolas", 14), wrap="word", bg="#fdfdfd", fg="#333")
        self.text_box.pack(expand=True, fill="both", padx=10, pady=10)
        self.text_box.config(state="disabled")

        # 状态栏
        self.status = ttk.Label(root, text="就绪", relief="sunken", anchor="w")
        self.status.pack(side="bottom", fill="x", padx=10, pady=(5, 0))

        # 绑定键事件
        self.text_box.bind("<Key>", self.on_key_press)
```

**功能**: 应用程序的主初始化方法，创建所有UI组件和核心对象

**详细说明**:

- 设置窗口标题、大小和主题样式
- 初始化三个核心组件:
  - `TypeWriter`: 处理文本文件和字符显示逻辑
  - `KeyboardMonitor`: 监控键盘事件和计算打字速度
  - `DataManager`: 管理测试数据的存储和检索
- 初始化统计变量:
  - `started`: 标记测试是否开始
  - `start_time/end_time`: 记录测试起止时间
  - `typed_chars/key_events`: 统计字符数和按键次数
- 构建用户界面:
  - 顶部工具栏按钮
  - 主文本显示区域（只读模式）
  - 底部状态栏
- 绑定键盘事件监听器



#### **`_reset_stats` - 重置统计**

```python
    def _reset_stats(self):
        self.started = False
        self.start_time = None
        self.end_time = None
        self.typed_chars = 0
        self.key_events = 0
        self.stopped = False
```

**功能**: 内部方法，重置所有统计变量到初始状态

**详细说明**:

- 重置开始/结束时间为 `None`
- 字符数和按键数归零
- 清除开始和停止标志
- 为新的测试会话做准备



#### **`focus_textbox` - 聚焦文本框**

```python
    def focus_textbox(self):
        self.text_box.focus_set()
        self.status.config(text="聚焦文本区，按任意字符键开始显示文本（功能键除外）")
```

**功能**: 将输入焦点设置到文本区域并更新状态提示

**详细说明**:

- 调用 `self.text_box.focus_set()` 确保文本框获得焦点
- 更新状态栏显示操作提示
- 这是开始打字测试的必要准备步骤



#### **`load_text` - 加载文本文件**

```python
    def load_text(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not file_path:
            return

        encoding = detect_encoding(file_path)
        if not encoding:
            self.status.config(text="无法识别文件编码")
            return

        # 重置统计并打开文件
        self._reset_stats()
        self.typewriter.open_file(file_path, encoding) # 调用typewriter包
        self.text_box.config(state="normal")
        self.text_box.delete("1.0", "end")
        self.text_box.config(state="disabled")
        self.status.config(text=f"已加载文件: {file_path} (编码: {encoding})\n提示：按任意键显示下一个字符。")
        self.focus_textbox()
```

**功能**: 打开文件对话框，选择并加载文本文件

**详细说明**:

1. 弹出文件选择对话框，限制文件类型为文本文件
2. 使用 `detect_encoding` 工具检测文件编码
3. 重置统计数据和文本显示区域
4. 调用 `TypeWriter.open_file()` 加载文件内容
5. 更新状态栏显示文件信息和操作提示
6. 自动调用 `focus_textbox()` 准备开始测试



#### **`on_key_press` - 键盘事件处理**

```python
    def on_key_press(self, event):
        # 仅在已加载文件时有效
        if not self.typewriter.loaded: # 调用typewriter包
            return "break"

        if self.stopped:
            return "break"

        ignore_keys = ("BackSpace", "Shift_L", "Shift_R", "Control_L", "Control_R",
                       "Alt_L", "Tab", "Escape", "Caps_Lock")

        # 第一次有效按键时启动计时与监控
        if not self.started:
            self.started = True
            self.start_time = time.time()
            self.keyboard_monitor.start_monitoring(self.handle_speed_alert)# 启动 KeyboardMonitor 并传入回调
            

        # 记录按键次数（有效）
        self.key_events += 1

        # 获取下一个字符
        char = self.typewriter.get_next_char() # 调用typewriter包
        if char is None:
            # 文件已读完
            self.end_time = time.time()
            self.stopped = True
            self._save_and_show_stats(finished=True)
            return "break"

        # 将字符插入到只读文本框中
        self.text_box.config(state="normal")
        self.text_box.insert("end", char)
        self.text_box.see("end")
        self.text_box.config(state="disabled")

        self.typed_chars += 1
        return "break"
```

**功能**: 处理所有键盘按键事件，驱动核心打字逻辑

**详细说明**:

- **条件检查**:
  - 确保已加载文件 (`self.typewriter.loaded`)
  - 测试未被停止 (`not self.stopped`)
  - 忽略功能键（Shift、Ctrl、Alt等）
- **启动逻辑**:
  - 第一个有效按键时启动计时器
  - 调用 `KeyboardMonitor.start_monitoring()` 开始监控
- **核心处理**:
  - 记录有效按键次数
  - 从 `TypeWriter` 获取下一个字符
  - 将字符插入到文本显示区域
  - 自动滚动到文本末尾
- **结束条件**:
  - 文件读取完成时自动结束



#### **`stop_and_show_stats` - 停止测试**

```python
    def stop_and_show_stats(self):
        if not self.started and not self.typewriter.loaded: # 调用typewriter包
            self.status.config(text="没有正在进行的会话，可先打开文件并按键开始。")
            return

        if not self.end_time:
            self.end_time = time.time()
        self.stopped = True

        self.keyboard_monitor.stop_monitoring()   # 停止监控
        self.typewriter.reset()# 关闭文件

        self._save_and_show_stats(finished=False)
```

**功能**: 手动停止当前测试并显示统计结果

**详细说明**:

- 检查测试状态，确保有正在进行的话动
- 设置结束时间标记
- 停止键盘监控 (`KeyboardMonitor.stop_monitoring()`)
- 重置 `TypeWriter` 状态
- 调用 `_save_and_show_stats()` 保存并显示结果





#### **`_compute_stats` - 计算统计数据**

```python
    def _compute_stats(self):
        total_time = 0.0
        if self.start_time and self.end_time:
            total_time = max(0.0, self.end_time - self.start_time)
        elif self.start_time and not self.end_time:
            total_time = max(0.0, time.time() - self.start_time)

        chars = self.typed_chars
        keys = self.key_events
        cps = chars / total_time 
        wpm = (chars / 5.0) / (total_time / 60.0) 

        return {
            "chars": chars,
            "keys": keys,
            "time_s": round(total_time, 2),
            "cps": round(cps, 2),
            "wpm": round(wpm, 2)
        }
```

**功能**: 内部方法，计算各种打字统计指标

**返回**: 包含统计信息的字典

**计算内容**:

- `total_time`: 总用时（秒）
- `chars`: 显示的字符总数
- `keys`: 有效按键次数
- `cps`: 每秒字符数 (Characters Per Second)
- `wpm`: 每分钟字数 (Words Per Minute)，按5字符=1词计算



#### **`_save_and_show_stats` - 保存和显示统计**

```python
    def _save_and_show_stats(self, finished=False):
        stats = self._compute_stats()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 尝试从 KeyboardMonitor 获取即时速度和按键总数
        try:
            current_speed = round(self.keyboard_monitor.get_current_speed(), 2) # 调用keyboard_monitor包
        except Exception:
            current_speed = round(stats["cps"] * 60, 2)  # fallback

        try:
            total_keystrokes = self.keyboard_monitor.get_total_keystrokes() # 调用keyboard_monitor包
        except Exception:
            total_keystrokes = stats["keys"]

        test_data = {
            "timestamp": timestamp,
            "speed": current_speed,
            "duration": stats["time_s"],
            "typed_chars": stats["chars"],
            "total_keystrokes": total_keystrokes,
            "wpm_estimated": stats["wpm"]
        }
        self.data_manager.save_test(test_data)# 保存到 data_manager
        
        # 构造显示消息并更新状态栏
        if finished:
            title = "完成 — 测试结束"
        else:
            title = "已停止 — 测试中断"

        msg = (f"显示字符: {stats['chars']}\n"
               f"用时(秒): {stats['time_s']}\n"
               f"即时速度(字/分): {current_speed}\n"
               f"估算 WPM: {stats['wpm']}")

        self.status.config(text=msg.replace("\n", " | "))
        self._show_nonblocking_alert(title, msg)
```

**功能**: 保存测试数据并显示统计结果

**参数**:

- `finished`: 布尔值，标记是否正常完成

**详细说明**:

1. 调用 `_compute_stats()` 获取统计数据
2. 从 `KeyboardMonitor` 获取实时速度和总按键数
3. 构建测试数据字典
4. 调用 `DataManager.save_test()` 保存数据
5. 更新状态栏显示关键统计信息
6. 显示非阻塞的通知弹窗



#### **`handle_speed_alert` - 速度提醒回调**

```python
    def handle_speed_alert(self, title, message):# KeyboardMonitor的回调函数的定义
        self.root.after(0, lambda: self._show_nonblocking_alert(title, message)) # 直接在主线程中显示弹窗

```

**功能**: `KeyboardMonitor` 的回调函数，处理速度提醒

**详细说明**:

- 由 `KeyboardMonitor` 在检测到速度异常时调用
- 使用 `root.after()` 确保在主线程中安全更新UI
- 调用 `_show_nonblocking_alert()` 显示提醒



#### **`_show_nonblocking_alert` - 非阻塞弹窗**

```python
    def _show_nonblocking_alert(self, title, message):
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)  # 去掉标题栏和边框
        popup.attributes("-topmost", True)

        # 内容框
        container = ttk.Frame(popup, padding=10)
        container.pack(fill="both", expand=True)

        # 标题与消息
        title_lbl = ttk.Label(container, text=title, font=("Arial", 10, "bold"))
        title_lbl.pack(anchor="w")
        msg_lbl = ttk.Label(container, text=message, font=("Arial", 9), wraplength=360, justify="left")
        msg_lbl.pack(anchor="w", pady=(4, 0))

        # 测量窗口大小
        popup.update_idletasks()
        win_w = popup.winfo_reqwidth()
        win_h = popup.winfo_reqheight()

        # 计算右上角位置
        screen_w = popup.winfo_screenwidth()
        margin_x = 20
        margin_y = 20
        x = screen_w - win_w - margin_x
        y = margin_y
        popup.geometry(f"{win_w}x{win_h}+{x}+{y}")

        # 确保不抢焦点
        # 2 秒后自动销毁
        popup.after(2000, popup.destroy)
```

**功能**: 显示不会阻塞主程序的临时通知窗口

**特性**:

- 无边框设计 (`overrideredirect(True)`)
- 始终置顶 (`attributes("-topmost", True)`)
- 自动定位在屏幕右上角
- 2秒后自动消失
- 不会抢夺输入焦点



#### **`show_data_dashboard` - 数据面板**

```python
    # 数据面板
    def show_data_dashboard(self):
        recent = self.data_manager.get_recent_tests(10) # 调用data_manager包

        dash = tk.Toplevel(self.root)
        dash.title("TypeFlow — 数据分析 / 历史记录")
        dash.geometry("700x500")

        frame = ttk.Frame(dash, padding=10)
        frame.pack(fill="both", expand=True)

        title_label = ttk.Label(frame, text="最近测试记录", font=("Arial", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))

        if not recent:
            ttk.Label(frame, text="暂无记录，开始一次测试后会在这里显示", foreground="gray").pack()
            return

        # 滚动显示区域
        canvas = tk.Canvas(frame, height=360)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for rec in recent:
            rec_text = (
                f"时间: {rec.get('timestamp','-')} | "
                f"即时速度(字/分): {rec.get('speed',0)} | "
                f"时长(s): {rec.get('duration',0)} | "
                f"显示字符: {rec.get('typed_chars',0)} | "
                f"按键总数: {rec.get('total_keystrokes',0)}"
            )
            lbl = ttk.Label(scroll_frame, text=rec_text, anchor="w")
            lbl.pack(fill="x", pady=4)

        # 底部按钮：清除历史
        btn_frame = ttk.Frame(dash, padding=8)
        btn_frame.pack(fill="x", side="bottom")
        ttk.Button(btn_frame, text="清除全部历史数据", bootstyle="danger-outline", command=lambda: self._confirm_clear_history(dash)).pack(side="right")
```

**功能**: 显示历史测试数据的管理面板

**详细说明**:

1. 从 `DataManager` 获取最近10次测试记录
2. 创建新窗口显示数据
3. 使用Canvas和Scrollbar实现滚动显示
4. 每条记录显示时间、速度、时长等完整信息
5. 底部提供清除历史数据按钮



#### **`_confirm_clear_history` - 确认清除历史**

```python
    def _confirm_clear_history(self, window_to_close=None):
        confirmed = messagebox.askyesno("确认", "确定要清除所有历史测试数据吗？此操作不可撤销。")
        if confirmed:
            try:
                self.data_manager.clear_all_data() # 调用data_manager包
                messagebox.showinfo("已清除", "历史数据已被清除。")
                # 关闭并重新打开面板
                if window_to_close:
                    window_to_close.destroy()
                    # 重新打开更新后的面板
                    self.show_data_dashboard()
            except Exception as e:
                messagebox.showerror("错误", f"清除数据失败：{e}")
```

**功能**: 显示确认对话框并清除所有历史数据

**详细说明**:

- 使用 `messagebox.askyesno()` 显示确认对话框
- 确认后调用 `DataManager.clear_all_data()` 清除数据
- 自动刷新数据面板显示
- 提供操作成功或失败的反馈



#### **`reset` - 重置应用状态**

```python
    def reset(self):
        self.typewriter.reset()

        self.text_box.config(state="normal")
        self.text_box.delete("1.0", "end")
        self.text_box.config(state="disabled")
        self.status.config(text="已重置")
        self._reset_stats()
        self.stopped = False
```

**功能**: 完全重置应用程序到初始状态

**详细说明**:

- 重置 `TypeWriter` 状态
- 清空文本显示区域
- 重置所有统计变量
- 更新状态栏显示重置完成信息



## 核心交互流程

### 正常测试流程:

1. `load_text()` → 选择并加载文件
2. `focus_textbox()` → 准备开始
3. `on_key_press()` → 处理每个按键，显示字符
4. `_save_and_show_stats()` → 保存结果并显示统计
5. `show_data_dashboard()` → 查看历史记录

### 数据流动:

- 键盘事件 → `on_key_press()`
- 字符获取 → `TypeWriter.get_next_char()`
- 速度监控 → `KeyboardMonitor` 回调
- 数据存储 → `DataManager.save_test()`
- 结果显示 → 状态栏和弹窗

每个方法都承担着明确的职责，共同构成了完整的打字测试应用程序。
