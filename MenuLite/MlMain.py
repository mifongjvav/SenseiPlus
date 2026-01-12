import logging
import coloredlogs
import json
import os
import shared_data
from MenuLite.Menu.MenuFunc import *  # noqa: F403

logging.basicConfig(level=logging.INFO)
coloredlogs.install(level="INFO", fmt="%(asctime)s - %(funcName)s: %(message)s")  # noqa: F821

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 构建配置文件的绝对路径
if shared_data.restricted:
    config_path = os.path.join(script_dir, './Menu/MlConfigRestricted.json')
else:
    config_path = os.path.join(script_dir, './Menu/MlConfig.json')

with open(config_path, encoding='utf-8') as file:
    config = json.load(file)

menu_items = config["menu_items"]

def ml_main_menu():
    # 直接遍历字典的键值对
    for key, value in menu_items.items():
        logging.info(key + '. ' + value)
    logging.info("x. 退出")

def ml_input():
    while True:
        try:
            logging.info("请输入菜单项: ")
            user_input = input()
            if user_input == 'x':
                logging.info("退出程序")
                os._exit(0)
            
            # 检查输入的键是否存在于menu_items中
            if user_input in menu_items:
                # 获取对应的函数名
                func_name = menu_items[user_input]
                # 使用globals()获取全局命名空间中的函数对象
                func = globals().get(func_name)
                
                if func and callable(func):
                    # 调用函数
                    func()
                else:
                    logging.error(f"函数 {func_name} 不存在或不可调用")
            else:
                logging.error(f"无效的键: {user_input}")
        except Exception as e:
            logging.error(f"发生错误: {str(e)}")