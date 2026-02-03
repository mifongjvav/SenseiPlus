import zipfile
import os
import requests
import logging
import json
from Main import Debug

def update():
    with zipfile.ZipFile(update_zip, 'r') as zf:
        root = zf.namelist()[0].split('/')[0] if zf.namelist() else ''
        for F in zf.infolist():
            if F.filename.startswith(root + '/'):
                target = F.filename.replace(root + '/', '', 1)
                if target and not F.is_dir():  # 跳过空路径和目录
                    # 只在有父目录时才创建
                    if '/' in target:
                        os.makedirs(target[:target.rfind('/')], exist_ok=True)
                    with open(target, 'wb') as out:
                        out.write(zf.read(F))
    os.remove(update_zip)

if Debug:
    update_zip = 'SenseiPlus-dev.zip'
    branch = 'dev'
else:
    update_zip = 'SenseiPlus-main.zip'
    branch = 'main'

build_info = requests.get(f'https://raw.githubusercontent.com/mifongjvav/SenseiPlus/{branch}/build_info.json', verify=False)

with open('build_info.json', 'r', encoding='utf-8') as f:
    build_info_file = json.load(f)

if build_info.json()['version'] != build_info_file['version']:
    logging.info(f"有新的版本 {build_info.json()['version']} 可用，正在下载更新...")
    
    try:
        download = requests.get(f'https://github.com/mifongjvav/SenseiPlus/archive/refs/heads/{branch}.zip', verify=False)
        # 保存下载的文件
        with open(update_zip, 'wb') as f:
            f.write(download.content)
        update()
        logging.info("更新完成")
        os._exit(0)
    except requests.RequestException as e:
        logging.error(f"无法下载更新文件: {e}")
        exit(1)

