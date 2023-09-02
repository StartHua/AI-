from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout  import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
from functools import partial
from kivy.uix.popup import Popup
import json
import os
from utils.util import * 
from assist.reptile_video import reptileMgr
import asyncio
import threading

# 导入新的模块
from config.tts_language import ttsLanguageMgr
from utils.encryption_util import *
from Plugins.FreeGPT import freeGPTMgr

class MyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.taskIsRuning = False  # 初始化属性
    
    def create_checkBox(self,size_hint,text,paddingLeft:int = 30):
        checkbox_area = BoxLayout(orientation='horizontal', size_hint=size_hint)
        # 创建horizontal，容纳复选框和标签，设置其对齐方式为左对齐、垂直居中
        vertical_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), width=checkbox_area.height + paddingLeft , padding=0)
        my_checkBox = CheckBox(size_hint=(None, None), active=False)
        checkbox1_label = Label(text=text, font_name=self.font_name, valign='middle')

        # 将复选框和标签添加到垂直布局中
        vertical_layout.add_widget(my_checkBox)
        vertical_layout.add_widget(checkbox1_label)

        checkbox_area.add_widget(vertical_layout)
        return my_checkBox,checkbox_area

    def numeric_filter(self, text, new_text):
        allowed_characters = "0123456789"  # 允许的数字字符
        return all(c in allowed_characters for c in new_text)

    
    def build(self):
        self.title = "二次创作短视频"
        # 设置中文字体
        font_name = CHINESE_FONT
        self.font_name = font_name  # 将字体名称保存在App的属性中

        # 从导入的模块中获取语言列表
        self.languages = ttsLanguageMgr.language

        layout = BoxLayout(orientation='horizontal')

        # 左边布局，分为上下两部分
        left_layout = BoxLayout(orientation='vertical', size_hint=(0.4, 1))

        # 上部分，Toggle按钮：男 女
        gender_layout = BoxLayout(size_hint=(1, 0.1))
        self.male_toggle = ToggleButton(text='男', group='gender', size_hint=(0.5, 1), font_name=self.font_name)
        self.female_toggle = ToggleButton(text='女', group='gender', size_hint=(0.5, 1), font_name=self.font_name)
        gender_layout.add_widget(self.male_toggle)
        gender_layout.add_widget(self.female_toggle)
        left_layout.add_widget(gender_layout)

        layout.add_widget(left_layout)

        # 右边布局
        right_layout = BoxLayout(orientation='vertical', size_hint=(0.6, 1))
        Temp = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        right_layout.add_widget(Temp)
        self.enable_secondary_creation_checkbox,checkbox_area = self.create_checkBox((1, 0.1),'开启二次创作') 
        right_layout.add_widget(checkbox_area)

        # 第二行复选框
        self.secondary_creation_options_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.secondary_creation_options_layout.opacity = 0  # 初始隐藏

        self.enable_gpt_checkbox,checkbox2_container = self.create_checkBox((1, 0.07),'gpt润色',10) 
        self.secondary_creation_options_layout.add_widget(checkbox2_container)
        
        self.enable_bg_music_checkbox,checkbox4_container = self.create_checkBox((1, 0.07),'背景音乐',10)
        self.secondary_creation_options_layout.add_widget(checkbox4_container)

        self.add_srt,checkbox_srt_container = self.create_checkBox((1, 0.07),'添加字幕',10)
        self.secondary_creation_options_layout.add_widget(checkbox_srt_container)

        right_layout.add_widget(self.secondary_creation_options_layout)
        
        # 第三行
        self.third_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.third_layout.opacity = 0  # 初始隐藏
        
        self.top_checkBox,checkbox5_container = self.create_checkBox((1, 0.07),'添加头尾',10)
        self.third_layout.add_widget(checkbox5_container)
        
        self.mark_checkBox,checkbox6_container = self.create_checkBox((1, 0.07),'水印图片左下',10)
        self.third_layout.add_widget(checkbox6_container)
        
        self.shu_video,checkbox7_container = self.create_checkBox((1, 0.07),'强制横屏',10)
        self.third_layout.add_widget(checkbox7_container)

        right_layout.add_widget(self.third_layout)
        
        # 开始结束
        layout1 = BoxLayout(orientation='horizontal', spacing=5, padding=10,size_hint=(1, 0.1))
        checkbox1_label = Label(text="删除开始(秒):", font_name=self.font_name, valign='middle')
        self.start_input = TextInput(hint_text='', size_hint=(None, None), width=80, height=30)
        # self.start_input.bind(on_text=self.numeric_filter)
        G = Label(text="删除结束(秒):", font_name=self.font_name, valign='middle')
        self.end_input = TextInput(hint_text='',font_name=self.font_name, size_hint=(None, None), width=80, height=30)
        # self.end_input.bind(on_text=self.numeric_filter)
        layout1.add_widget(checkbox1_label)
        layout1.add_widget(self.start_input )
        layout1.add_widget(G )
        layout1.add_widget(self.end_input )
        right_layout.add_widget(layout1)
        
        
        # 提示词输入框
        self.input_area = BoxLayout(orientation='horizontal', size_hint=(1, None))  # 调整提示词输入框高度
        self.input_text = TextInput(size_hint=(None, None), width=500, hint_text='提示词', font_name=self.font_name)  # 设置宽度为300，添加提示文字
        self.input_area.opacity = 0  # 初始隐藏
        self.input_area.add_widget(self.input_text)
        right_layout.add_widget(self.input_area)

        # 中间区域，大的TextInput
        self.middle_input = TextInput(size_hint=(1, 0.6), multiline=True, font_name=self.font_name)
        right_layout.add_widget(self.middle_input)

        # 底部区域，两个按钮
        bottom_area = BoxLayout(size_hint=(1, 0.1))
        save_button = Button(text='保存配置', size_hint=(0.3, 1), font_name=self.font_name)
        delButton = Button(text='删除二创视频', size_hint=(0.3, 1), font_name=self.font_name)
        start_button = Button(text='启动下载', size_hint=(0.4, 1), font_name=self.font_name)
        bottom_area.add_widget(save_button)
        bottom_area.add_widget(delButton)
        bottom_area.add_widget(start_button)
        right_layout.add_widget(bottom_area)

        layout.add_widget(right_layout)

        self.male_toggle.bind(on_press=self.on_male_toggle)
        self.female_toggle.bind(on_press=self.on_female_toggle)
        save_button.bind(on_press=self.save_config)
        delButton.bind(on_press=self.del_video)
        start_button.bind(on_press=self.start_download)
        self.enable_secondary_creation_checkbox.bind(active=self.on_secondary_creation_checkbox_active)
        self.enable_gpt_checkbox.bind(active=self.on_gpt_checkbox_active)
        

     
        # 下部分，滚动区域根据Toggle选择显示数据
        self.checkboxes_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.scroll_view = ScrollView(size_hint=(1, None), height=500)
        self.scroll_view.add_widget(self.checkboxes_layout)
        left_layout.add_widget(self.scroll_view)
        if os.path.exists("config.json"):
          with open("config.json", "r") as f:
            config_data = json.load(f)
            selected_gender = config_data.get("selected_gender", 0)
            if selected_gender == 0:
                self.male_toggle.state = "down"
                self.female_toggle.state = "normal"
                self.on_male_toggle(self.male_toggle)
            elif selected_gender == 1:
                self.male_toggle.state = "normal"
                self.female_toggle.state = "down"
                self.on_female_toggle(self.female_toggle)
            if self.enable_secondary_creation_checkbox:
                self.enable_secondary_creation_checkbox.active = config_data.get("enable_secondary_creation", False)
            if self.enable_gpt_checkbox:
                self.enable_gpt_checkbox.active = config_data.get("enable_gpt", False)
            if self.enable_bg_music_checkbox:
                self.enable_bg_music_checkbox.active = config_data.get("enable_bg_music", False)
            if self.input_text:
                self.input_text.text = config_data.get("input_text", "")
            if self.middle_input:
                self.middle_input.text = config_data.get("middle_input", "")
                
            if self.top_checkBox:
                self.top_checkBox.active = config_data.get("enable_top_video", False)
            if self.mark_checkBox:
                self.mark_checkBox.active = config_data.get("enable_mark", False)
            if self.shu_video:
                self.shu_video.active = config_data.get("enable_shu_video", False)     
            if self.start_input:
                self.start_input.text = config_data.get("cut_start", "")   
            if self.end_input:
                self.end_input.text = config_data.get("cut_end", "") 
            if self.add_srt:
                self.add_srt.active = config_data.get("add_srt", False)    
               
            selected_languages = config_data.get("selected_languages", [])
            for checkbox_container in self.checkboxes_layout.children:
                label = checkbox_container.children[0]
                if label.text in selected_languages:
                    checkbox = checkbox_container.children[1]
                    if isinstance(checkbox, CheckBox):
                        checkbox.active = True
        return layout
      
      
    def on_male_toggle(self, instance):
        if self.male_toggle.state == "normal" and self.female_toggle.state == "normal":
            # 如果都未选中，则默认选择男性
            self.male_toggle.state = "down"
        elif self.male_toggle.state == "down":
            self.update_checkboxes('Male')

    def on_female_toggle(self, instance):
        if self.male_toggle.state == "normal" and self.female_toggle.state == "normal":
            # 如果都未选中，则默认选择女性
            self.female_toggle.state = "down"
        elif self.female_toggle.state == "down":
            self.update_checkboxes('Female')


    def update_checkboxes(self, selected_gender):
        self.checkboxes_layout.clear_widgets()

        for language in self.languages:
            if language['Gender'] == selected_gender:
                checkbox_label = f"{language['country']} ({language['cn']})"
                checkbox_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
                checkbox = CheckBox(active=False, size_hint_x=None, width=30)
                checkbox_label_widget = Label(text=checkbox_label, font_name=self.font_name)
                checkbox_container.add_widget(checkbox)
                checkbox_container.add_widget(checkbox_label_widget)
                self.checkboxes_layout.add_widget(checkbox_container)

        # 调整GridLayout的高度
        self.checkboxes_layout.height = len(self.checkboxes_layout.children) * (30 + 5)

    def on_secondary_creation_checkbox_active(self, instance, value):
        if value:
            self.secondary_creation_options_layout.opacity = 1
            self.third_layout.opacity = 1
            if self.enable_gpt_checkbox.active:
                self.input_area.opacity = 1
        else:
            self.secondary_creation_options_layout.opacity = 0
            self.third_layout.opacity = 0
            self.input_area.opacity = 0

    def on_gpt_checkbox_active(self, instance, value):
        if value and self.enable_secondary_creation_checkbox.active:
            self.input_area.opacity = 1
        else:
            self.input_area.opacity = 0

    def del_video(self,instance):
        if not os.path.exists(Download_Path):
            return
        dirs = os.listdir(Download_Path)
        for item in dirs:
            p = Download_Path + "/" + item
            itemDirs = os.listdir(p)
            for vItem in itemDirs:
                vPath = p+"/"+vItem
                if os.path.exists(vPath) and os.path.isdir(vPath):
                    files = os.listdir(vPath)
                    for file in files:
                        file_extension = os.path.splitext(file)[1]
                        if file_extension.lower() == ".mp4":
                            delete_file(vPath + "/" +file)
                    
    
    def save_config(self, instance):
        selected_languages = []
        for checkbox_container in self.checkboxes_layout.children:
            checkbox = checkbox_container.children[1]  # 获取Toggle按钮部件

            if isinstance(checkbox, CheckBox) and checkbox.active:  # 确保是Toggle按钮部件且处于按下状态
                label = checkbox_container.children[0]  # 获取标签部件
                selected_languages.append(label.text)
        
        config_data = {
           "selected_gender": 0 if self.male_toggle.state == "down" else 1,
            "enable_secondary_creation": self.enable_secondary_creation_checkbox.active,
            "enable_gpt": self.enable_gpt_checkbox.active,
            "enable_bg_music": self.enable_bg_music_checkbox.active,
            "input_text": self.input_text.text,
            "middle_input": self.middle_input.text,
            "selected_languages": selected_languages,
            "enable_top_video":self.top_checkBox.active,
            "enable_mark":self.mark_checkBox.active,
            "enable_shu_video":self.shu_video.active,
            "cut_start":self.start_input.text,
            "cut_end":self.end_input.text,
            "add_srt":self.add_srt.active
        }
        with open('config.json', 'w') as f:
            json.dump(config_data, f)

    def show_running_popup(self, msg):
         # 创建一个 BoxLayout 作为整体布局
        overall_layout = BoxLayout(orientation='vertical')

        # 创建一个 Label，作为内容，设置文本和字体大小
        content_label = Label(text=msg, font_size=16,font_name=self.font_name)

        overall_layout.add_widget(content_label)

        # 创建 Popup 对象，设置整体布局作为内容部分，并设置大小
        popup = Popup(title=" Tip ", title_align="center", content=overall_layout, size_hint=(None, None), size=(300, 200))

        # 打开 Popup
        popup.open()
    
    def on_download_complete_gui(self,msg):
        self.taskIsRuning = False 
        self.show_running_popup(msg)
        
    def on_download_complete(self):
        Clock.schedule_once(lambda dt: self.on_download_complete_gui("Over~~~~"), 0.1)

    def is_number(self,s):
        return s.isdigit()
        
    def start_download(self, instance):
        # 检查是否是数字
        if self.start_input.text == "":
            self.start_input.text = "0"
        if self.end_input.text == "":
            self.end_input.text = "0"    
        if(not self.is_number(self.start_input.text) ):
            self.show_running_popup("截取开始只能填写数字！")  
            return
        if(not self.is_number(self.end_input.text)):
            self.show_running_popup("截取结束只能填写数字！")  
            return   
        cut_start = int(self.start_input.text)
        cut_end = int(self.end_input.text)
                
        if self.taskIsRuning:
            print("正在运行~~~")
            self.show_running_popup("正在运行~~~~")
            return
        self.taskIsRuning = True
        
        # 检查key
        # keyState,msg = decrypt_aes_uuid()
        # if keyState ==False:
        #     self.show_running_popup(msg)
        #     return

        def download_task():
            loop = asyncio.new_event_loop()  # 创建一个新的事件循环
            asyncio.set_event_loop(loop)  # 设置新的事件循环为当前线程的事件循环

            async def async_download():
                urls = find_url(self.middle_input.text)
                selected_languages = []
                for checkbox_container in self.checkboxes_layout.children:
                    checkbox = checkbox_container.children[1]
                    if isinstance(checkbox, CheckBox) and checkbox.active:
                        label = checkbox_container.children[0]
                        for language in self.languages:
                            checkbox_label = f"{language['country']} ({language['cn']})"
                            if checkbox_label == label.text:
                                selected_languages.append(language)

                task = reptileMgr.batch_download_file(
                    urls,
                    self.enable_secondary_creation_checkbox.active,
                    selected_languages,
                    self.enable_gpt_checkbox.active,
                    self.input_text.text,
                    self.enable_bg_music_checkbox.active,
                    self.top_checkBox.active,
                    self.mark_checkBox.active,
                    self.add_srt.active,
                    self.shu_video.active,
                    cut_start,
                    cut_end
                )

                await task
                loop.call_soon_threadsafe(self.on_download_complete)  # 在主线程中调用下载完成的操作

            loop.run_until_complete(async_download())
            loop.close()

        threading.Thread(target=download_task).start()


if __name__ == '__main__':
    # currId = get_machine_code()
    # print(currId)
    # end_time = offset_date_curtime(5)
    # s.t = freeGPTMgr.call("你好")
    MyApp().run()


