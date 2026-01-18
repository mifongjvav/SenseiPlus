import logging
import coloredlogs
import requests
from fake_useragent import UserAgent
import datetime
import pickle
import os
import json
import getpass
from MenuLite.Menu.api import PostAPI

logging.basicConfig(level=logging.INFO)
coloredlogs.install(level="INFO", fmt="%(asctime)s - %(funcName)s: %(message)s")

'''======-配置区-======'''
post_ids = []
TOKEN_START_INDEX = 99  # 从第几个token开始（0表示第一个）
MAX_REPORTS_PER_TOKEN = 5  # 每个token每天最多举报5个帖子
MAX_DAILY_TOTAL_REPORTS = 100  # 每天最多总举报次数
'''===================='''

class DailyReportLimiter:
    """每日举报次数限制器"""
    def __init__(self, limit_file="report_limit.pkl"):
        self.limit_file = limit_file
        self.today = datetime.date.today().isoformat()
        self.load_data()
    
    def load_data(self):
        """加载历史数据"""
        try:
            if os.path.exists(self.limit_file):
                with open(self.limit_file, 'rb') as f:
                    data = pickle.load(f)
                    # 检查是否是今天的数据
                    if data.get("date") == self.today:
                        self.today_count = data.get("count", 0)
                    else:
                        self.today_count = 0
            else:
                self.today_count = 0
        except Exception as e:
            logging.error(f"加载每日举报次数限制器数据时出错: {e}")
            self.today_count = 0
    
    def save_data(self):
        """保存数据"""
        try:
            data = {"date": self.today, "count": self.today_count}
            with open(self.limit_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logging.error(f"保存每日举报次数限制器数据时出错: {e}")
    
    def can_report(self):
        """检查是否还可以举报"""
        return self.today_count < MAX_DAILY_TOTAL_REPORTS
    
    def increment(self):
        """增加举报计数"""
        if self.can_report():
            self.today_count += 1
            self.save_data()
            return True
        return False
    
    def get_remaining(self):
        """获取剩余可举报次数"""
        return max(0, MAX_DAILY_TOTAL_REPORTS - self.today_count)
    
    def get_today_info(self):
        """获取今日举报信息"""
        return {
            "date": self.today,
            "count": self.today_count,
            "limit": MAX_DAILY_TOTAL_REPORTS,
            "remaining": self.get_remaining()
        }

# 初始化每日限制器
daily_limiter = DailyReportLimiter()
today_info = daily_limiter.get_today_info()
logging.info(f"今日 [{today_info['date']}] 已举报 {today_info['count']} 次，剩余 {today_info['remaining']} 次")

# 检查今日是否已达上限
if not daily_limiter.can_report():
    logging.error(f"今日已达最大举报限制 {MAX_DAILY_TOTAL_REPORTS} 次，请明天再试")
    exit(0)

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
    except KeyError:
        logging.error("登录响应中没有找到用户信息")
        exit(1)

    logging.info(f"登录成功，用户ID: {login_user_id}")
    # 将用户登录信息写入login.json
    with open("login.json", "w", encoding="utf-8") as f:
        f.write(login_response.text)

logging.info("请输入要举报的帖子标题")
title = input()
logging.info("请输入举报详情")
detail = input()

report_detail = detail + f" | 使用Argon批量举报帖子工具举报 | 使用者用户ID: {login_user_id}"

logging.info("为防止滥用，我们会将您的用户ID包含在举报详情中，确定要继续吗？(y/n)")
confirm = input()
if confirm.lower() != 'y':
    logging.info("操作已取消")
    exit(0)

# 先获取第一页数据，获取总帖子数
first_page_response = requests.get(f"https://api.codemao.cn/web/forums/posts/search?title={title}&limit=30&page=1")
first_page_data = first_page_response.json()
total = first_page_data['total']

if total == 0:
    logging.info("没有找到相关帖子")
    exit(0)

logging.info(f"找到 {total} 条相关帖子")

# 计算总页数（每页30条）
total_pages = (total + 30 - 1) // 30  # 向上取整

# 处理第一页的帖子
post_ids.extend([item['id'] for item in first_page_data['items']])

# 如果有多页，获取后续页面的数据
for page in range(2, total_pages + 1):
    response = requests.get(f"https://api.codemao.cn/web/forums/posts/search?title={title}&limit=30&page={page}")
    page_data = response.json()
    post_ids.extend([item['id'] for item in page_data['items']])
    logging.info(f"已获取第 {page} 页，当前共 {len(post_ids)} 个帖子")

# 检查帖子数量是否超过今日剩余举报次数
remaining_before = daily_limiter.get_remaining()
if len(post_ids) > remaining_before:
    logging.warning(f"找到 {len(post_ids)} 个帖子，但今日只能再举报 {remaining_before} 次")
    post_ids = post_ids[:remaining_before]  # 只处理剩余可举报的数量

# 打印所有 id
print("所有帖子的 ID：")
for post_id in post_ids:
    print(post_id)

print(f"\n共找到 {len(post_ids)} 个帖子，将处理其中 {min(len(post_ids), remaining_before)} 个")
print(f"全部 ID 列表：{post_ids}")

# 读取token
with open('./tokens.txt', "r") as f:
    TokenList = [line.strip() for line in f if line.strip()]

if not TokenList:
    logging.error("tokens.txt 中没有找到有效的 token")
    exit(0)

# 检查起始索引是否有效
if TOKEN_START_INDEX >= len(TokenList):
    logging.error(f"起始索引 {TOKEN_START_INDEX} 超出token列表范围 (0-{len(TokenList)-1})")
    exit(0)

logging.info(f"共读取到 {len(TokenList)} 个 token，从第 {TOKEN_START_INDEX + 1} 个开始")

# 初始化每个token的举报计数
token_reports_count = {token: 0 for token in TokenList}
current_token_index = TOKEN_START_INDEX
total_reported = 0

logging.info("开始举报帖子")
for post_id in post_ids:
    # 检查每日总限制
    if not daily_limiter.can_report():
        logging.warning(f"今日已达最大举报限制 {MAX_DAILY_TOTAL_REPORTS} 次，停止举报")
        break
    
    # 循环查找可用的token
    start_index = current_token_index
    token_found = False
    
    while True:
        current_token = TokenList[current_token_index]
        
        # 检查这个token是否还可以举报
        if token_reports_count[current_token] < MAX_REPORTS_PER_TOKEN:
            # 使用这个token举报
            token_found = True
            break
        
        # 这个token已经达到上限，尝试下一个
        current_token_index = (current_token_index + 1) % len(TokenList)
        
        # 如果已经循环了一圈，说明所有token都达到上限
        if current_token_index == start_index:
            break
    
    # 如果找不到可用的token，停止举报
    if not token_found:
        logging.warning(f"所有token都已达到每日上限 {MAX_REPORTS_PER_TOKEN} 个，停止举报")
        break
    
    # 使用找到的token举报
    report = PostAPI('/web/reports/posts', {
        "post_id": post_id,
        "description": report_detail,
        "reason_id": 1
    }, Token=current_token)
    
    # 更新计数
    token_reports_count[current_token] += 1
    total_reported += 1
    
    # 更新每日总限制
    if daily_limiter.increment():
        logging.info(f"使用 token[{current_token_index}] (已举报{token_reports_count[current_token]}/{MAX_REPORTS_PER_TOKEN}次) 举报帖子 {post_id} 响应：{report.json()}")
        logging.info(f"今日已举报 {daily_limiter.today_count}/{MAX_DAILY_TOTAL_REPORTS} 次，剩余 {daily_limiter.get_remaining()} 次")
    else:
        logging.error("增加每日计数失败，可能已达到上限")
        break
    
    # 移动到下一个token
    current_token_index = (current_token_index + 1) % len(TokenList)

# 输出统计信息
logging.info(f"举报完成，共成功举报 {total_reported} 个帖子")
today_final_info = daily_limiter.get_today_info()
logging.info(f"今日最终统计: 已举报 {today_final_info['count']}/{today_final_info['limit']} 次")

logging.info("每个token的举报统计：")
for i, token in enumerate(TokenList):
    count = token_reports_count[token]
    if count > 0:
        logging.info(f"  token[{i}]: {count}/{MAX_REPORTS_PER_TOKEN} 个")