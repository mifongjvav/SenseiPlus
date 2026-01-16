import logging
import threading
import os
import shared_data
import getpass

try:
    import CodemaoEDUTools
except ImportError:
    logging.error("请执行以下命令安装CodemaoEDUTools：")
    logging.info("pip install CodemaoEDUTools")
    os._exit(1)

ids = shared_data.ids

threads = []

class Func:
    def ReportAllWorks():
        logging.info("开始举报作品（多线程）")
        for work_id in ids:
            thread = threading.Thread(
                target=CodemaoEDUTools.ReportWork,
                args=('./tokens.txt', work_id, '违法违规', '1')
            )
            threads.append(thread)
            thread.start()

    def LikeAllWorks():
        logging.info("开始点赞作品（多线程）")
        for work_id in ids:
            thread = threading.Thread(
                target=CodemaoEDUTools.LikeWork,
                args=('./tokens.txt', work_id)
            )
            threads.append(thread)
            thread.start()

    def CollectAllWorks():
        logging.info("开始收藏作品（多线程）")
        for work_id in ids:
            thread = threading.Thread(
                target=CodemaoEDUTools.CollectionWork,
                args=('./tokens.txt', work_id)
            )
            threads.append(thread)
            thread.start()

    def ReviewAllWorks():
        logging.info("开始评论作品（多线程）")
        for work_id in ids:
            thread = threading.Thread(
                target=CodemaoEDUTools.SendReviewToWork,
                args=('./tokens.txt', work_id, '这是一条评论')
            )
            threads.append(thread)
            thread.start()

    def ViewAllWorks():
        logging.info("开始浏览所有作品（多线程）")
        for work_id in ids:
            CodemaoEDUTools.ViewWork('./tokens.txt', work_id)

    def GenerateStudentList():
        logging.info("生成学生列表")
        student_list = shared_data.generate_strings(count=100, length=8)
        logging.info(student_list)

    def BRP():
        os.system("python BRP.py")

    def AddIToken():
        logging.info("输入用户名/手机号")
        Username = input()
        logging.info("输入密码，不会显示")
        Password = getpass.getpass()
        Token = CodemaoEDUTools.GetUserToken(Username, Password)
        if Token:
            with open('./tokens.txt', 'a', encoding='utf-8') as f:
                f.write(Token + '\n')
            logging.info(f"Token {Token} 已添加到tokens.txt")
        else:
            logging.error("获取Token失败")
    
    def Logout():
        os.remove("login.json")
        logging.info("已退出登录")