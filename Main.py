import json
import logging
import coloredlogs
import requests
import os
import threading
import random
import string
try:
    import CodemaoEDUTools
except ImportError:
    logging.error("请执行以下命令安装CodemaoEDUTools：")
    logging.info("pip install CodemaoEDUTools")
    os._exit(1)

logging.basicConfig(level=logging.INFO)
coloredlogs.install(level="INFO", fmt="%(asctime)s - %(funcName)s: %(message)s")

script_dir = os.getcwd()
current_dir = os.path.dirname(os.path.abspath(__file__))

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
'''
try:
    from main import ReportWork, LikeWork, CollectionWork, SendReviewToWork, ViewWork
except ImportError:
    logging.error("无法导入CodemaoEDUTools，请确保CodemaoEDUTools与SenseiPlus在同一目录下")
    os._exit(1)
'''

if script_dir != current_dir:
    os.chdir(current_dir)
    logging.warning(f"工作目录并非脚本所在目录，已切换工作目录到当前目录: {current_dir}")

if not os.path.exists('./tokens.txt'):
    open('./tokens.txt', 'w').close()

if len(open('./tokens.txt', 'r').readlines()) == 0:
    logging.error("你没有任何token，请先获取token")
    logging.info("请执行：")
    logging.info("python main.py login-edu -i <含有账号密码的xlsx表格文件的路径> -o <*.txt> -s <是否同时签署友好协议{True/False}>")
    os._exit(1)

# 主程序
logging.info("请输入用户ID，输入0退出:")
user_id = input()
if user_id == "0":
    os._exit(0)

response = requests.get(f'https://api.codemao.cn/creation-tools/v1/user/center/work-list?user_id={user_id}&offset=0&limit=4999')
workids = json.loads(response.text)
try:
    ids = [item['id'] for item in workids['items']]
except KeyError:
    logging.error("此用户ID不存在或该用户没有作品")
    os._exit(1)
logging.info(f"总共找到 {len(ids)} 个作品ID")
logging.info("token数：" + str(len(open('./tokens.txt', 'r').readlines())))

logging.info("选择方法:")
logging.info("1. 举报所有作品")
logging.info("2. 点赞所有作品")
logging.info("3. 收藏所有作品")
logging.info("4. 评论所有作品")
logging.info("5. 浏览所有作品")
logging.info("6. 生成学生列表")
logging.info("7. 退出")
logging.info("请输入方法编号:")
method = input()

if method == "7":
    logging.info("退出程序")
    os._exit(0)

# 创建线程列表
threads = []

if method == "1":
    logging.info("开始举报作品（多线程）")
    for work_id in ids:
        # 创建线程，直接调用原函数
        thread = threading.Thread(
            target=CodemaoEDUTools.ReportWork,  # 要执行的函数
            args=('./tokens.txt', work_id, '违法违规', '1')  # 函数的参数
        )
        threads.append(thread)
        thread.start()
elif method == "2":
    logging.info("开始点赞作品（多线程）")
    for work_id in ids:
        thread = threading.Thread(
            target=CodemaoEDUTools.LikeWork,
            args=('./tokens.txt', work_id)
        )
        threads.append(thread)
        thread.start()
elif method == "3":
    logging.info("开始收藏作品（多线程）")
    for work_id in ids:
        thread = threading.Thread(
            target=CodemaoEDUTools.CollectionWork,
            args=('./tokens.txt', work_id)
        )
        threads.append(thread)
        thread.start()
elif method == "4":
    logging.info("请输入评论内容:")
    review_content = input()
    logging.info("开始评论作品（多线程）")
    for work_id in ids:
        thread = threading.Thread(
            target=CodemaoEDUTools.SendReviewToWork,
            args=('./tokens.txt', work_id, review_content)
        )
        threads.append(thread)
        thread.start()
elif method == "5":
    logging.info("开始浏览作品（多线程）")
    for work_id in ids:
        thread = threading.Thread(
            target=CodemaoEDUTools.ViewWork,
            args=('./tokens.txt', work_id)
        )
        threads.append(thread)
        thread.start()
elif method == "6":
    logging.info("生成学生列表")
    student_list = generate_strings(count=100, length=8)
    logging.info(student_list)
else:
    logging.error("请输入正确的方法")
    os._exit(0)

if method in ["1", "2", "3", "4", "5"]:
    # 等待所有线程完成
    logging.info(f"已启动 {len(threads)} 个线程，请等待处理完成...")
    for thread in threads:
        thread.join()

logging.info("全部操作完成")