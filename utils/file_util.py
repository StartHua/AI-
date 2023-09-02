#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/7/31
@Author  : chengXingHua
@File    : fileUtil.py
@content : 文件工具
"""
import os
import shutil
import json


# 创建文件夹
def create_dir(dir: str):
    if os.path.exists(dir):
        return False
    os.makedirs(dir)
    return True


# 删除文件夹
def delete_dir(dir: str):
    if not os.path.exists(dir):
        return False
    shutil.rmtree(dir)
    return True


# 写入json保存本地
def save_json(filePath: str, fileObject):
    if not filePath.endswith(".json"):
        filePath = filePath + ".json"
    dir_name = os.path.dirname(filePath)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    if os.path.isfile(filePath):
        os.remove(filePath)
    with open(filePath, 'w', encoding='utf-8') as f:
        s = json.dumps(fileObject)
        f.write(s)


# 上传本地文件
def upload_local_file(path, file):
    if not file:
        return False, "文件不能为空！"
    if not os.path.exists(path):
        return False, "不存在！"
    kfile = os.path.join(path, file.filename)
    if os.path.exists(kfile):
        return False, "文件已存在！"
    file.save(kfile)
    return True, "上传成功！"


# 删除文件
def delete_file(path):
    if not os.path.exists(path):
        return False, "文件不存在！"
    os.remove(path)
    return True, "删除成功！"

