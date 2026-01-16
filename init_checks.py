# config.py 或 init_checks.py
import os
import sys
import logging

def check_python_version():
    """检查Python版本"""
    major, minor = sys.version_info[:2]
    if major != 3 or minor < 9:
        logging.error(f"Python版本必须为3.9及以上，当前版本为{major}.{minor}")
        return False
    return True

def check_working_directory():
    """检查工作目录"""
    script_dir = os.path.normcase(os.getcwd())
    current_dir = os.path.normcase(os.path.dirname(os.path.abspath(__file__)))
    
    if script_dir != current_dir:
        os.chdir(current_dir)
        logging.warning(f"工作目录并非脚本所在目录，已切换工作目录到当前目录: {current_dir}")
    return current_dir

def check_tokens_file():
    """检查tokens文件"""
    if not os.path.exists('./tokens.txt'):
        open('./tokens.txt', 'w').close()
    
    with open('./tokens.txt', 'r') as f:
        lines = f.readlines()
        if len(lines) == 0:
            logging.error("你没有任何token，请先获取token")
            logging.info("请执行：")
            logging.info("python main.py login-edu -i <含有账号密码的xlsx表格文件的路径> -o <*.txt> -s <是否同时签署友好协议{True/False}>")
            return False
    return True

def perform_all_checks():
    """执行所有检查"""
    if not check_python_version():
        return False
    
    check_working_directory()
    
    if not check_tokens_file():
        return False
    
    return True