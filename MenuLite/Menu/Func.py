import logging
import threading
import os
import shared_data
import getpass
import requests
import json
import sys
import time
from .cetextra import UnTopReview
from .api import GetAPI, PostAPI
from fake_useragent import UserAgent
def top_comment(selected_id, work_id):
    logging.info(f"正在置顶评论 {selected_id}...")
    # 设置token为第一个token
    with open('./tokens.txt', 'r', encoding='utf-8') as f:
        tokens = f.readlines()
        if tokens:
            token = tokens[0].strip()
        else:
            logging.error("tokens.txt 中没有可用的token")
            return
    try:
        # 假设CodemaoEDUTools中有置顶函数
        CodemaoEDUTools.TopReview(token, work_id, selected_id)
        logging.info(f"评论 {selected_id} 置顶成功！")
    except Exception as e:
        logging.error(f"置顶失败：{e}")

def PutAPI(Path: str, Token: str, json_data: dict = None) -> requests.Response:
    """PUT方式调用API"""
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "User-Agent": UserAgent().random,
        "authorization": Token,
    }
    return requests.put(url=f"https://api-creation.codemao.cn{Path}", headers=headers, json=json_data)

try:
    import CodemaoEDUTools
except ImportError:
    import CodemaoEDUTools
    logging.error("请执行以下命令安装CodemaoEDUTools：")
    logging.info("pip install CodemaoEDUTools")
    os._exit(1)

ids = shared_data.ids

threads = []

class Func:
    @staticmethod
    def ReportAllWorks():
        logging.info("开始举报作品（多线程）")
        for work_id in ids:
            thread = threading.Thread(
                target=CodemaoEDUTools.ReportWork,
                args=('./tokens.txt', work_id, '违法违规', '1')
            )
            threads.append(thread)
            thread.start()

    @staticmethod
    def LikeAllWorks():
        logging.info("开始点赞作品（多线程）")
        for work_id in ids:
            thread = threading.Thread(
                target=CodemaoEDUTools.LikeWork,
                args=('./tokens.txt', work_id)
            )
            threads.append(thread)
            thread.start()

    @staticmethod
    def CollectAllWorks():
        logging.info("开始收藏作品（多线程）")
        for work_id in ids:
            thread = threading.Thread(
                target=CodemaoEDUTools.CollectionWork,
                args=('./tokens.txt', work_id)
            )
            threads.append(thread)
            thread.start()

    @staticmethod
    def ReviewAllWorks():
        logging.info("开始评论作品（多线程）")
        for work_id in ids:
            thread = threading.Thread(
                target=CodemaoEDUTools.SendReviewToWork,
                args=('./tokens.txt', work_id, '这是一条评论')
            )
            threads.append(thread)
            thread.start()

    @staticmethod
    def ViewAllWorks():
        logging.info("开始浏览所有作品（多线程）")
        for work_id in ids:
            CodemaoEDUTools.ViewWork('./tokens.txt', work_id)

    @staticmethod
    def GenerateStudentList():
        logging.info("生成学生列表")
        student_list = shared_data.generate_strings(count=100, length=8)
        logging.info(student_list)

    @staticmethod
    def BRP():
        os.system("python BRP.py")

    @staticmethod
    def AddToken():
        logging.info("输入用户名/手机号，输入0使用当前登录用户")
        username = input()
        if username == '0':
            with open('./login.json', 'r', encoding='utf-8') as f:
                login_data = json.load(f)
                token = login_data['auth']['token']
        else:
            logging.info("输入密码，不会显示")
            password = getpass.getpass()
            token = CodemaoEDUTools.GetUserToken(username, password)
        if token:
            with open('./tokens.txt', 'a', encoding='utf-8') as f:
                f.write(token + '\n')
            logging.info(f"token {token} 已添加到tokens.txt")
        else:
            logging.error("获取Token失败")
    
    @staticmethod
    def SearchAndPinComment():
        logging.info("输入要搜索的作品ID")
        work_id = input()
        logging.info("输入要搜索的评论内容")
        comment_content = input()
        
        # 获取评论总数
        comment = requests.get(f"https://api.codemao.cn/creation-tools/v1/works/{work_id}/comments?offset=0&limit=101")
        if comment.status_code != 200:
            logging.error(f"获取评论失败，状态码：{comment.status_code}")
            return
        
        total_comments = comment.json().get('total', 0)
        logging.info(f"总评论数：{total_comments}")
        
        all_comments = []
        current_offset = 0
        
        # 自动翻页获取所有评论
        while current_offset < total_comments:
            url = f"https://api.codemao.cn/creation-tools/v1/works/{work_id}/comments?offset={current_offset}&limit=101"
            comment = requests.get(url)
            
            if comment.status_code == 200:
                page_comments = comment.json().get('items', [])
                all_comments.extend(page_comments)
                logging.info(f"已获取 {current_offset + len(page_comments)}/{total_comments} 条评论")
            else:
                logging.error(f"获取评论失败，状态码：{comment.status_code}")
                break
            
            current_offset += 101
        
        # 筛选包含指定内容的评论
        matching_comments = []
        for comment in all_comments:
            content = comment.get('content', '')
            if comment_content.lower() in content.lower():
                matching_comments.append(comment)
        
        if not matching_comments:
            logging.info(f"未找到包含 '{comment_content}' 的评论")
            return
        
        logging.info(f"找到 {len(matching_comments)} 条匹配的评论：")
        logging.info("=" * 50)
        
        # 显示所有匹配的评论
        for i, comment in enumerate(matching_comments, 1):
            comment_id = comment.get('id', '')
            content = comment.get('content', '')[:50] + "..." if len(comment.get('content', '')) > 50 else comment.get('content', '')
            is_top = comment.get('is_top', False)
            top_status = "已置顶" if is_top else "未置顶"
            
            logging.info(f"{i}. ID: {comment_id}")
            logging.info(f"   内容: {content}")
            logging.info(f"   状态: {top_status}")
            logging.info("-" * 40)
        
        # 让用户选择要要置顶/取消置顶的评论
        logging.info("输入要置顶/取消置顶的评论ID（或输入0取消）：")
        selected_id = input()
        
        if selected_id == "0":
            logging.info("操作已取消")
            return
        
        # 查找选中的评论
        selected_comment = None
        for comment in matching_comments:
            if str(comment.get('id', '')) == selected_id:
                selected_comment = comment
                break
        
        if not selected_comment:
            logging.error(f"未找到ID为 {selected_id} 的评论")
            return
        
        # 检查是否已置顶
        if selected_comment.get('is_top', False):
            # 执行取消置顶操作
            logging.info(f"正在取消置顶评论 {selected_id}...")
            # 设置token为第一个token
            with open('./tokens.txt', 'r', encoding='utf-8') as f:
                tokens = f.readlines()
                if tokens:
                    token = tokens[0].strip()
                else:
                    logging.error("tokens.txt 中没有可用的token")
                    return
            if UnTopReview(token, work_id, selected_id):
                logging.info(f"评论 {selected_id} 取消置顶成功！")
            else:
                logging.error(f"取消置顶评论 {selected_id} 失败")

        else:
            # 执行置顶操作
            top_comment(selected_id, work_id)

    @staticmethod
    def Logout():
        os.remove("login.json")
        logging.info("已退出登录")
        sys.exit()

    @staticmethod
    def CleanNewMessages():
        with open('login.json', 'r', encoding='utf-8') as f:
            login_data = json.load(f)
        token = login_data['auth']['token']
        
        # 三种消息类型
        message_types = [
            ("COMMENT_REPLY", "评论回复"),
            ("LIKE_FORK", "点赞/分享"),
            ("SYSTEM", "系统消息")
        ]
        
        for query_type, type_name in message_types:
            logging.info(f"开始清理{type_name}消息...")
            
            all_messages = []
            current_offset = 0
            limit = 200  # 每次获取200条
            
            while True:
                url = f"/web/message-record?query_type={query_type}&limit={limit}&offset={current_offset}"
                response = GetAPI(url, token)
                
                if response.status_code != 200:
                    logging.error(f"获取{type_name}消息失败，状态码：{response.status_code}")
                    break
                
                data = response.json()
                page_messages = data.get('items', [])
                total_messages = data.get('total', 0)
                
                # 如果是第一次请求，显示总消息数
                if current_offset == 0:
                    logging.info(f"{type_name}消息总数：{total_messages}")
                
                # 添加当前页的消息
                all_messages.extend(page_messages)
                
                # 显示进度
                retrieved_count = current_offset + len(page_messages)
                logging.info(f"已获取 {type_name} 消息 {retrieved_count}/{total_messages} 条")
                
                # 如果没有更多消息，或者已经获取了所有消息，退出循环
                if len(page_messages) == 0 or retrieved_count >= total_messages:
                    break
                
                # 增加 offset 以获取下一页
                current_offset += limit
            
            # 输出获取到的消息数量
            logging.info(f"共获取到{type_name}消息 {len(all_messages)} 条")
            
            logging.info(f"{type_name}消息获取完成")
    @staticmethod
    def     PublishCustomCoCoWork():
        with open('login.json', 'r', encoding='utf-8') as f:
            login_data = json.load(f)
        token = login_data['auth']['token']
        logging.info("请输入作品ID")
        work_id = input()
        logging.info("请输入自定义url")
        custom_url = input()
        logging.info("请输入作品名称")
        name = input()
        logging.info("请输入作品描述")
        description = input()
        logging.info("请输入操作说明")
        operation = input()
        json_data = {
    "name": name,
    "description": description,
    "operation": operation,
    "cover_url": "https://creation.bcmcdn.com/716/appcraft/IMAGE_Ujly7Ixj4_1769251346032",
    "bcmc_url": "https://creation.bcmcdn.com/716/appcraft/JSON_b8Q6O3S5m_1769251346363.json",
    "player_url": custom_url
        }
        response = PutAPI(f"/coconut/web/work/{work_id}/publish", token, json_data)
        logging.info(f"发布作品 {work_id} 为自定义URL {custom_url} 响应状态码：{response.status_code}")

    @staticmethod
    def CommentAndTop():
        logging.info('输入评论内容')
        comment_content = input()
        comment_content = str(comment_content)
        logging.info('输入作品ID')
        work_id = input()
        comment_data = {
            "emoji_content": "",
            "content": comment_content
        }
        with open('login.json', 'r', encoding='utf-8') as f:
            login_data = json.load(f)
            login_token = login_data['auth']['token']
        response = PostAPI(f"/creation-tools/v1/works/{work_id}/comment", comment_data, login_token)
        if response.status_code != 201:
            if response.json()['error_message'] == '当前作品评论额度用完啦！看看其他作品吧~':
                logging.error("评论失败，评论额度用完")
                return
        selected_id = response.json()['id']
        time.sleep(1)  # 等待1秒以确保评论已发布
        top_comment(selected_id, work_id)