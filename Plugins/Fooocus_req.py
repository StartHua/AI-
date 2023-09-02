import os
import json
from config.config import *
from gradio_client import Client
import shutil

class Fooocus_mgr:
    def __init__(self) -> None:
        self.conf = []

    def read_ui_config(self):
        conf = os.path.join(UP_PROJECT_PATH,"config/fooocus_config.json")
        if os.path.exists(conf):
            with open(conf, 'r') as f:
                my_list = json.load(f)     
            return my_list     
        return None  

    def call(self,save_path,prompt,size,style = "cinematic-default"):
        conf = self.read_ui_config()
        conf[0] = prompt
        conf[4] = size
        conf[2] = style
        client = Client("http://127.0.0.1:7860/")
        client.serialize = False
        result = client.predict(
                *conf,
                fn_index=4
        )
        # 获取最后一个字典中'value'键的值，它是一个列表
        value_list = result[-1]['value']

        # 获取列表中的最后一个元素，它是一个字典
        last_dict = value_list[-1]

        # 获取这个字典中'name'键的值
        image_path = last_dict['name']
        print("图片:" + image_path)
        # 使用 shutil.move() 将图片移动到目标路径并改名
        shutil.move(image_path, save_path)
        
fooocusMgr = Fooocus_mgr()