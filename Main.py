import logging
import coloredlogs
import os
import requests
import json
import random
import string
import shared_data

logging.basicConfig(level=logging.INFO)
coloredlogs.install(level="INFO", fmt="%(asctime)s - %(funcName)s: %(message)s")

def generate_strings(count=1, length=8):
    if length > 26:
        return []
    
    result = []
    
    for _ in range(count):
        # 随机选择起始位置
        max_start = 26 - length
        start = random.randint(0, max_start)
        
        # 从该位置开始取连续字母
        string_part = string.ascii_lowercase[start:start + length]
        result.append(string_part)
    
    return result

# 主程序
logging.info("请输入用户ID，输入0退出，输入1使用受限模式:")
user_id = input()
if user_id == "0":
    os._exit(0)
elif user_id == "1":
    shared_data.restricted = True
else:
    shared_data.restricted = False
    response = requests.get(f'https://api.codemao.cn/creation-tools/v1/user/center/work-list?user_id={user_id}&offset=0&limit=4999')
    workids = json.loads(response.text)
    try:
        shared_data.ids = [item['id'] for item in workids['items']]  # 存储到共享模块
    except KeyError:
        logging.error("此用户ID不存在或该用户没有作品")
        os._exit(1)
    logging.info(f"总共找到 {len(shared_data.ids)} 个作品ID")
    logging.info("token数：" + str(len(open('./tokens.txt', 'r').readlines())))

from MenuLite.MlMain import ml_main_menu, ml_input  # noqa: E402

ml_main_menu()
ml_input()
