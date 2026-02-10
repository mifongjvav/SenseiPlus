import requests
import json
from datetime import datetime, timezone, timedelta

owner = "mifongjvav"
repo = "SenseiPlus"
version = "3.0.0b"

def get_latest_commit_sha(owner_func, repo_func, short=True, branch=None):
    if branch:
        url = f"https://api.github.com/repos/{owner_func}/{repo_func}/commits/{branch}"
    else:
        url = f"https://api.github.com/repos/{owner_func}/{repo_func}/commits"
    
    response = requests.get(url, verify=False)
    response.raise_for_status()
    
    if branch:
        sha = response.json()["sha"]
    else:
        sha = response.json()[0]["sha"]
    
    if short:
        return sha[:7]
    return sha

def get_build_date():
    # UTC+8 时区
    utc8 = timezone(timedelta(hours=8))
    now_utc8 = datetime.now(utc8)
    return now_utc8.strftime("%Y-%m-%d %H:%M:%S")

short_sha = get_latest_commit_sha(owner, repo, short=True)

build_info = {
    "commit": short_sha,
    "build_date": get_build_date(),
    "version": version
}

with open("build_info.json", "w", encoding="utf-8") as f:
    json.dump(build_info, f, indent=4, ensure_ascii=False)

print("✅ 已生成 build_info.json")