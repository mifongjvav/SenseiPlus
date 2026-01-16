import logging
import coloredlogs
import os
import requests
import json
import random
import string
import shared_data
import sys
import getpass
from fake_useragent import UserAgent
from init_checks import perform_all_checks
from MenuLite.MlMain import set_condition_var

# 配置全局 logging
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "latest.log")
try:
    import CodemaoEDUTools
except ImportError:
    logging.error("请执行以下命令安装CodemaoEDUTools：")
    logging.info("pip install CodemaoEDUTools")
    os._exit(1)

# 删除脚本所在目录下的latest.log文件，不会误删除
try:
    os.remove(os.path.join(os.path.dirname(__file__), "latest.log"))
except FileNotFoundError:
    pass

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ],
)
coloredlogs.install(level="DEBUG", fmt="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s")
perform_all_checks()

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

short_sha =json.load(open("build_info.json", "r", encoding="utf-8"))["commit"]
build_date = json.load(open("build_info.json", "r", encoding="utf-8"))["build_date"]

# 主程序
logging.info(f'''
███████╗███████╗███╗   ██╗███████╗███████╗██╗██████╗ ██╗     ██╗   ██╗███████╗
██╔════╝██╔════╝████╗  ██║██╔════╝██╔════╝██║██╔══██╗██║     ██║   ██║██╔════╝
███████╗█████╗  ██╔██╗ ██║███████╗█████╗  ██║██████╔╝██║     ██║   ██║███████╗
╚════██║██╔══╝  ██║╚██╗██║╚════██║██╔══╝  ██║██╔═══╝ ██║     ██║   ██║╚════██║
███████║███████╗██║ ╚████║███████║███████╗██║██║     ███████╗╚██████╔╝███████║
╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝╚═╝     ╚══════╝ ╚═════╝ ╚══════╝
-==============================================================================-
欢迎使用SenseiPlus

Author：Argon
Version：{json.load(open("build_info.json", "r", encoding="utf-8"))["version"]}
提交：{short_sha}
构建日期：{build_date}
-==============================================================================-
''')
if os.path.exists("login.json"):
    try:
        with open("login.json", "r", encoding="utf-8") as f:
            login_data = json.load(f)
            login_user_name = login_data['user_info']['nickname']
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        logging.warning(f"login.json 文件损坏或格式错误: {e}")
        # 删除损坏的文件，重新登录
        os.remove("login.json")
        login_user_name = None
else:
    logging.info("登录到Codemao Network以使用SenseiPlus")
    logging.info("请输入您的用户名/手机号")
    identity = input()
    logging.info("请输入您的密码")
    password = getpass.getpass()
    try:
        login_response = requests.post(
            url="https://api.codemao.cn/tiger/v3/web/accounts/login",
            headers={
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "User-Agent": UserAgent().random,
            },
            json={
            "pid": "65edCTyg",
            "identity": identity,
            "password": password
            }
        )
    except requests.RequestException as e:
        logging.error(f"登录请求失败: {e}")
        exit(1)

    logging.info(f"登录响应状态码: {login_response.status_code}")
    logging.info(f"登录响应内容: {login_response.text}")
    try:
        login_user_id = login_response.json()['user_info']['id']
        login_user_name = login_response.json()['user_info']['nickname']
    except KeyError:
        logging.error("登录响应中没有找到用户信息")
        exit(1)

    logging.info(f"登录成功，用户ID: {login_user_id}")
    # 将用户登录信息写入login.json
    with open("login.json", "w", encoding="utf-8") as f:
        f.write(login_response.text)
logging.info(f"欢迎回家，sensei {login_user_name}")

logging.info("请输入对方的用户ID，输入0退出，输入1使用受限模式:")
user_id = input()
if user_id == "0":
    sys.exit(0)
elif user_id == "1":
    shared_data.restricted = True
    set_condition_var("restricted", True)
else:
    shared_data.restricted = False
    set_condition_var("restricted", False)
    response = requests.get(f'https://api.codemao.cn/creation-tools/v1/user/center/work-list?user_id={user_id}&offset=0&limit=4999')
    workids = json.loads(response.text)
    try:
        shared_data.ids = [item['id'] for item in workids['items']]  # 存储到共享模块
    except KeyError:
        logging.error("此用户ID不存在或该用户没有作品")
        sys.exit(1)
    logging.info(f"总共找到 {len(shared_data.ids)} 个作品ID")
    logging.info("token数：" + str(len(open('./tokens.txt', 'r').readlines())))

from MenuLite.MlMain import ml_input  # noqa: E402

ml_input()
