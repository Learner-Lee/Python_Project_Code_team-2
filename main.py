import ttkbootstrap as ttk # GUI 库
from ui import TypeWriterApp

if __name__ == "__main__":
    root = ttk.Window(themename="flatly") # 设置主题 "flatly"
    app = TypeWriterApp(root) # 实例化你的应用，把窗口 root 传进去
    root.mainloop()
