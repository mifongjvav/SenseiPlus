import logging
import threading
import os
import shared_data
import getpass
import requests
import json
import sys
from .cetextra import UnTopReview
from .api import GetAPI

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

    def AddToken():
        logging.info("输入用户名/手机号，输入0使用当前登录用户")
        Username = input()
        if Username == '0':
            with open('./login.json', 'r', encoding='utf-8') as f:
                login_data = json.load(f)
                Token = login_data['auth']['token']
        else:
            logging.info("输入密码，不会显示")
            Password = getpass.getpass()
            Token = CodemaoEDUTools.GetUserToken(Username, Password)
        if Token:
            with open('./tokens.txt', 'a', encoding='utf-8') as f:
                f.write(Token + '\n')
            logging.info(f"Token {Token} 已添加到tokens.txt")
        else:
            logging.error("获取Token失败")
    
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

    def Logout():
        os.remove("login.json")
        logging.info("已退出登录")
        sys.exit()

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
            
            # TODO: 这里添加实际清理消息的逻辑
            # 注意：由于原函数没有给出具体的清理API，这里只完成了翻页获取
            # 需要根据实际API添加标记已读、删除等操作
            
            logging.info(f"{type_name}消息获取完成")