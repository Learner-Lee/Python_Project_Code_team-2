# 补丁
def detect_encoding(file_path):
    """尝试检测文件编码"""
    encodings = ["utf-8", "gbk", "gb2312", "latin1"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                f.read(1024) # 试读一点
            return enc
        except UnicodeDecodeError:
            continue
    return None
