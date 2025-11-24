class TypeWriter:
    def __init__(self):
        self.file_handle = None     # 文件对象（未打开时为 None）
        self.buffer = ""            # 当前缓冲区内容    
        self.buffer_start_pos = 0   # 缓冲区在文件中的起始位置
        self.current_file_pos = 0   # 当前读取位置
        self.loaded = False         # 是否已加载文件

    def open_file(self, file_path, encoding):
        self.file_handle = open(file_path, "r", encoding=encoding, buffering=8192) # 设置缓冲区大小
        self.buffer = ""
        self.buffer_start_pos = 0
        self.current_file_pos = 0
        self.loaded = True

    # 获取下一个字符
    def get_next_char(self):
        if self.file_handle is None:
            return None

        # 是否超出缓冲区范围
        if self.current_file_pos - self.buffer_start_pos >= len(self.buffer):
            chunk = self.file_handle.read(4096)
            if not chunk:
                self.close()
                return None
            self.buffer = chunk # 保存新缓冲区内容
            self.buffer_start_pos = self.current_file_pos # 更新缓冲区起始位置

        idx_in_buffer = self.current_file_pos - self.buffer_start_pos # 计算在缓冲区中的索引
        char = self.buffer[idx_in_buffer] # 弹出当前文字
        self.current_file_pos += 1  # 索引到下一个位置
        return char

    def reset(self):
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
        self.current_file_pos = 0
        self.loaded = False
