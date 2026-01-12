import logging
import coloredlogs
import threading
import os
import shared_data
from init_checks import perform_all_checks
try:
    import CodemaoEDUTools
except ImportError:
    logging.error("请执行以下命令安装CodemaoEDUTools：")
    logging.info("pip install CodemaoEDUTools")
    os._exit(1)

logging.basicConfig(level=logging.INFO)
coloredlogs.install(level="INFO", fmt="%(asctime)s - %(funcName)s: %(message)s")

__all__ = ['举报所有作品', '点赞所有作品', '收藏所有作品', '评论所有作品', '浏览所有作品', '生成学生列表', '批量举报帖子']

perform_all_checks()

ids = shared_data.ids

threads = []

def 举报所有作品():
    logging.info("开始举报作品（多线程）")
    for work_id in ids:
        thread = threading.Thread(
            target=CodemaoEDUTools.ReportWork,
            args=('./tokens.txt', work_id, '违法违规', '1')
        )
        threads.append(thread)
        thread.start()

def 点赞所有作品():
    logging.info("开始点赞作品（多线程）")
    for work_id in ids:
        thread = threading.Thread(
            target=CodemaoEDUTools.LikeWork,
            args=('./tokens.txt', work_id)
        )
        threads.append(thread)
        thread.start()

def 收藏所有作品():
    logging.info("开始收藏作品（多线程）")
    for work_id in ids:
        thread = threading.Thread(
            target=CodemaoEDUTools.CollectionWork,
            args=('./tokens.txt', work_id)
        )
        threads.append(thread)
        thread.start()

def 评论所有作品():
    logging.info("开始评论作品（多线程）")
    for work_id in ids:
        thread = threading.Thread(
            target=CodemaoEDUTools.SendReviewToWork,
            args=('./tokens.txt', work_id, '这是一条评论')
        )
        threads.append(thread)
        thread.start()

def 浏览所有作品():
    logging.info("开始浏览所有作品（多线程）")
    for work_id in ids:
        thread = threading.Thread(
            target=CodemaoEDUTools.ViewWork,
            args=('./tokens.txt', work_id)
        )
        threads.append(thread)
        thread.start()

def 生成学生列表():
    logging.info("生成学生列表")
    student_list = shared_data.generate_strings(count=100, length=8)
    logging.info(student_list)

def 批量举报帖子():
    os.system("python BRP.py")