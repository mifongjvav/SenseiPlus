import logging
import getpass
import coloredlogs
import requests
import json
import os
import shared_data
from fake_useragent import UserAgent
coloredlogs.install(level="INFO", fmt="%(asctime)s - %(funcName)s: %(message)s")

def sp_login():
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
def sp_login_json():
    try:
        with open("login.json", "r", encoding="utf-8") as f:
            login_data = json.load(f)
            shared_data.login_user_name = login_data['user_info']['nickname']
            shared_data.login_token = login_data['auth']['token']
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        logging.warning(f"login.json 文件损坏或格式错误: {e}")
        # 删除损坏的文件，重新登录
        os.remove("login.json")
        shared_data.login_user_name = None