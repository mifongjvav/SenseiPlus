import logging
import json
import os
import shared_data
from MenuLite.Menu.MenuFunc import *  # noqa: F403

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 构建配置文件的绝对路径
config_path = os.path.join(script_dir, './Menu/MlConfig.json')

with open(config_path, encoding='utf-8') as file:
    config = json.load(file)

menu_items = config["menu_items"]

def check_conditions(conditions):
    """检查条件是否满足"""
    if not conditions:
        return True, None
    
    for key, required_value in conditions.items():
        current_value = shared_data.condition_vars.get(key)
        if current_value != required_value:
            return False, {key: required_value}
    
    return True, None

def ml_main_menu():
    """显示主菜单，根据条件过滤显示项 - 只显示可用的选项"""
    for key, item_info in menu_items.items():
        # 获取菜单项名称
        item_name = item_info.get("name", "未命名菜单项")
        
        # 检查条件
        conditions = item_info.get("conditions", {})
        conditions_met, _ = check_conditions(conditions)
        
        # 只显示条件满足的菜单项
        if conditions_met:
            logging.info(f"{key}. {item_name}")
    
    logging.info("x. 退出")

def ml_input():
    while True:
        try:
            ml_main_menu()
            logging.info("请输入菜单项: ")
            user_input = input().strip()
            
            if user_input == 'x':
                logging.info("退出程序")
                os._exit(0)
            
            # 检查输入的键是否存在于menu_items中
            if user_input in menu_items:
                item_info = menu_items[user_input]
                item_name = item_info.get("name", "未命名菜单项")
                func_name = item_name  # 假设函数名与菜单项名称相同
                
                # 检查条件是否满足
                conditions = item_info.get("conditions", {})
                conditions_met, failed_condition = check_conditions(conditions)
                
                if not conditions_met:
                    failed_key, required_value = next(iter(failed_condition.items()))
                    current_value = shared_data.condition_vars.get(failed_key, "未设置")
                    logging.error(f"功能 '{item_name}' 受到限制")
                    logging.error(f"条件不满足: {failed_key} 需要为 '{required_value}'，当前为 '{current_value}'")
                    logging.info("请先满足条件后再使用此功能")
                    continue
                
                # 获取对应的函数对象
                func = globals().get(func_name)
                
                if func and callable(func):
                    # 调用函数
                    logging.info(f"执行功能: {item_name}")
                    func()
                else:
                    logging.error(f"函数 {func_name} 不存在或不可调用")
            else:
                logging.error(f"无效的键: {user_input}")
        except KeyboardInterrupt:
            logging.info("\n用户中断操作")
            os._exit(0)
        except Exception as e:
            logging.error(f"发生错误: {str(e)}")

def set_condition_var(key, value):
    """设置条件变量（可以在其他模块中调用）"""
    shared_data.condition_vars[key] = value

def show_condition_vars():
    """显示当前所有条件变量"""
    logging.info("当前条件变量状态:")
    for key, value in shared_data.condition_vars.items():
        logging.info(f"  {key}: {value}")

# 防止重复执行的主程序入口
if __name__ == "__main__":
    # 确保条件变量字典存在
    if not hasattr(shared_data, 'condition_vars'):
        shared_data.condition_vars = {}
    
    # 运行主输入循环
    ml_input()