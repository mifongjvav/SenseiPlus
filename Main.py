import logging
import coloredlogs
import os
import requests
import json
import random
import string
import shared_data
import sys
import time
import subprocess
from init_checks import perform_all_checks
from MenuLite.MlMain import set_condition_var
from MenuLite.Menu.api import GetAPI
from login import sp_login, sp_login_json

Debug = True

if "__compiled__" in globals():
    shared_data.is_nuitka = True
    set_condition_var("is_nuitka", True)
else:
    shared_data.is_nuitka = False
    set_condition_var("is_nuitka", False)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 配置全局 logging
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "latest.log")

log_file = os.path.join(os.path.dirname(__file__), "latest.log")

# 如果有现有的日志处理器，先关闭它们
for handler in logging.root.handlers[:]:
    handler.close()
    logging.root.removeHandler(handler)

# 删除脚本所在目录下的latest.log文件，不会误删除
try:
    os.remove(os.path.join(os.path.dirname(__file__), "latest.log"))
except FileNotFoundError:
    pass
except PermissionError:
    restarted = True

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ],
)
if Debug:
    coloredlogs.install(level="DEBUG", fmt="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s")
else:
    coloredlogs.install(level="INFO", fmt="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s")
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


if __name__ == '__main__':
    short_sha = json.load(open("build_info.json", "r", encoding="utf-8"))["commit"]
    build_date = json.load(open("build_info.json", "r", encoding="utf-8"))["build_date"]
    version = json.load(open("build_info.json", "r", encoding="utf-8"))["version"]

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
    Email：smmomm@126.com
    Version：{version}
    提交：{short_sha}
    提交日期：{build_date}
    -==============================================================================-
    ''')
    if 'restart' in sys.argv or '--restart' in sys.argv:
        logging.warning("你似乎执行了重启操作，为保证工作继续，日志没有删除（其实是因为权限问题awa）")
    if os.path.exists("login.json"):
        sp_login_json()
    else:
        logging.info("登录到Codemao Network以使用SenseiPlus")
        sp_login()
        sp_login_json()
    logging.info(f"欢迎回家，{shared_data.login_user_name}")
    messages = GetAPI('/web/message-record/count', shared_data.login_token)
    messages = messages.json()
    counts = []
    for item in messages:
        if "count" in item:
            counts.append(item["count"])

    if counts[0] > 0 or counts[1] > 0 or counts[2] > 0:
        logging.warning("您有新消息，可以使用'10. 清除新消息通知'清除")
        logging.info(f"新回复数量: {counts[0]} 个")
        logging.info(f"新点赞/再创作数量: {counts[1]} 个")
        logging.info(f"新系统通知数量: {counts[2]} 个")

    # 记录登录时间的文件路径
    LOGIN_TIME_FILE = "login_time.json"

    # 获取当前时间戳
    current_time = time.time()

    # 如果存在 login_time.json 文件
    if os.path.exists(LOGIN_TIME_FILE):
        try:
            with open(LOGIN_TIME_FILE, "r", encoding="utf-8") as f:
                login_time_data = json.load(f)

            # 检查是否有 login_time 键
            if "login_time" in login_time_data:
                last_login_time = login_time_data["login_time"]
                time_diff_hours = (current_time - last_login_time) / 3600

                # 如果时间差大于72小时
                if time_diff_hours > 72:
                    logging.warning("为防止用户信息更改，SenseiPlus推荐你每72小时重新登录一次")
        except (json.JSONDecodeError, KeyError) as e:
            logging.debug(f"login_time.json 文件读取错误: {e}")
            # 文件损坏，创建新的
            pass

    # 无论是否存在文件，都更新当前登录时间
    try:
        with open(LOGIN_TIME_FILE, "w", encoding="utf-8") as f:
            json.dump({"login_time": current_time}, f)
    except Exception as e:
        logging.debug(f"写入登录时间失败: {e}")

    logging.info("请输入对方的用户ID，输入0退出，输入1使用受限模式:")
    try:
        user_id = input()
    except KeyboardInterrupt:
        logging.info("检测到疑似重复运行，正在重启")
        subprocess.run([sys.executable] + sys.argv + ["--restart"])
        sys.exit(0)
    if "&" in user_id or "python" in user_id:
        logging.info('检测到疑似重复运行，正在重启')
        subprocess.run([sys.executable] + sys.argv + ["--restart"])
        sys.exit(0)
    if user_id == "0":
        sys.exit(0)
    elif user_id == "1":
        shared_data.restricted = True
        set_condition_var("restricted", True)
    else:
        shared_data.restricted = False
        set_condition_var("restricted", False)
        response = requests.get(
            f'https://api.codemao.cn/creation-tools/v1/user/center/work-list?user_id={user_id}&offset=0&limit=4999')
        work_ids = json.loads(response.text)
        try:
            shared_data.ids = [item['id'] for item in work_ids['items']]  # 存储到共享模块
        except KeyError:
            logging.error("此用户ID不存在或该用户没有作品")
            sys.exit(1)
        logging.info(f"总共找到 {len(shared_data.ids)} 个作品ID")
        logging.info("token数：" + str(len(open('./tokens.txt', 'r').readlines())))

    from MenuLite.MlMain import ml_input  # noqa: E402

    ml_input()
