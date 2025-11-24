import json
import os
from datetime import datetime

class DataManager:

    def __init__(self, data_file_name="typing_data.json"):# 初始化数据管理器

        # 保存数据的文件路径
        self.data_file_path = data_file_name
        
        # 存储所有历史测试数据的列表
        self.all_test_data = []
        
        # 程序启动时自动加载历史数据
        self.load_data()
    
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
    
    def get_recent_tests(self, count=5):# 获取最近的测试记录

        # 如果历史数据为空，返回空列表
        if not self.all_test_data:
            return []
        
        # 获取最后count条记录，并反转顺序（最新的在前面）
        recent_tests = list(reversed(self.all_test_data[-count:]))
        return recent_tests
    
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
    
    def get_total_test_count(self):#获取总测试次数

        return len(self.all_test_data)
