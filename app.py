import gradio as gr
import argparse
from config.config import *
from config.tts_language import ttsLanguageMgr
import threading
import json
from utils.util import *
from assist.VideoDownloader import VideoDownloader

languages = ttsLanguageMgr.language

conf_path = "./config/save_conf.json"

#组件
male_row =None
Female_row =None  
second_row =None
prompt_txt = None
sd_row = None

# 创建 VideoDownloader 实例
downloader = VideoDownloader(max_workers=1)

# 回调函数示例
def on_download_complete(url):
    print(f"视频 {url} 下载已完成！")
   
    

def on_all_download_complete(args):
    print("全部下载完成！")
    # print(args)
     # 二次创作

# 读取配置
video_list_c = ""
voice_radio_c =  "男"
Male_select_c = []
Female_select_c =  []
second_checkBox_c =  False
use_gpt_c = False
use_sd_c =  False
prompt_txt_c =  ""
add_bg_sound_c = False
add_mark_c = False
add_srt_c =False
add_hear_bottom_c =False
force_v_c =  False
del_hear_c = False
del_bottom_c = False
sd_radio_c ="1280×768"
sd_prompt_txt_c = ""
cut_width_c = 1
cut_height_c = 1
sd_user_source_v_c = False
if os.path.exists(conf_path):
    with open(conf_path, 'r', encoding='utf-8') as file:
        content = file.read()
        conf = json.loads(content)
        print(conf)
        [video_list_c,           #视频列表
            voice_radio_c,       #语言选择
            Male_select_c,       #男语言
            Female_select_c,     #女语言
            second_checkBox_c,   #开启二次创作
            use_gpt_c,           #开始GPT润色
            use_sd_c,            #开启SD创作
            prompt_txt_c,        #提示词
            add_bg_sound_c,      #添加背景
            add_mark_c,          #添加水印
            add_srt_c,           #添加字幕
            add_hear_bottom_c,   #添加头尾
            force_v_c,           #强制横屏
            del_hear_c,          #删除头
            del_bottom_c,        #删除尾
            sd_radio_c,          #sd视频输出比例
            sd_prompt_txt_c,      #sd提示词
            cut_width_c,
            cut_height_c,
            sd_user_source_v_c
    ] = conf

del_hear_c = validate_numeric_input(del_hear_c)
if del_hear_c == None :
    del_hear_c = 0
del_bottom_c = validate_numeric_input(del_bottom_c)
if del_bottom_c == None :
    del_bottom_c = 0
if prompt_txt_c == "":
    prompt_txt_c = COM_PROMPT      
# 保存配置
def save_clicked(*args):
    print("保存配置@@")
    with open(conf_path, 'w',encoding='utf-8') as f:
        json.dump(args, f)

def del_video_clicked():
    print("删除二创视频！")        

def generate_clicked(*args):
    print("点击启动@@@")
    save_clicked(*args)
    print(list(args))
    generate_in_thread(*args)
    return

def generate_in_thread(*args):
    # 在新线程中运行生成代码的逻辑
    # 你可以在这里编写生成逻辑，然后在适当的时候更新界面
    print("在新线程中运行生成逻辑...")
    [       g_video_list,        #视频列表      0
            g_voice_radio,       #语言选择      1
            g_Male_select,       #男语言        2
            g_Female_select,     #女语言        3
            g_secondheckBox,     #开启二次创作  4
            g_use_gpt,           #开始GPT润色   5
            g_use_sd,            #开启SD创作    6
            g_prompt_txt,        #提示词        7
            g_add_bg_sound,      #添加背景      8
            g_add_mark,          #添加水印      9
            g_add_srt,           #添加字幕      10
            g_add_hear_bottom,   #添加头尾      11
            g_force_v,           #强制横屏      12
            g_del_hear,          #删除头        13
            g_del_bottom,         #删除尾       14
            g_sd_radio,           #sd视频输出比例15
            g_sd_prompt_txt,      #sd 提示词     16
            g_cut_width,          #保留裁剪视频宽 17
            g_cut_height,          #保留裁剪视频高 18
            g_sd_user_source_v    #使用原声音 19
    ] = args
    urls = find_url(g_video_list)
    downloader.download_all(urls,args)
    # 更新界面或执行其他操作

# 在 "公共设置" 标签中添加一个事件处理函数，用于监听 use_gpt 复选框的状态变化
def use_changed(value):
    pass
    # print("状态变化：", value)
    
# 开启二次创作
def open_second_fn(open):
    return second_row.update(visible=open)

# 开始GPT使用提示词
def use_gpt_fn(open):
    return prompt_txt.update(visible=open)

# Male Female
def getConryByGender(gender):
    temp = []
    for language in languages:
        if language['Gender'] == gender:
            checkbox_label = f"{language['country']} ({language['cn']})"
            temp.append(checkbox_label)
    return temp   

# 选择男女语言
def checkbox_visibility(selected_gender):
    if selected_gender == '男':
        return [True, False]  # 显示check1男，隐藏check2女
    else:
        return [False, True]  # 显示check2女，隐藏check1男

# 选择视频输出比例
def update_sd_checkbox(select):
    return sd_row.update(visible=select)
    
def update_checkbox_visibility(selected_gender):
    visibility = checkbox_visibility(selected_gender)
    return male_row.update(visible=visibility[0]),Female_row.update(visible=visibility[1])

isopen = False    
gradio_root = gr.Blocks(title=TITLE)
with gradio_root:
    with gr.Row():
        with gr.Column():
            video_list = gr.Textbox(label="视频链接",info="支持多条链接,支持youtobe,titko,抖音,B站",lines=30,max_lines = 30,value=video_list_c,)
        with gr.Column(scale=0.6, visible=True):            
            with gr.Tab(label='公共设置'):
                use_sd = gr.Checkbox(label='开启SD创作', value=use_sd_c)
                with gr.Column(visible = use_sd_c) as sd_row:
                        sd_radio = gr.Radio(['1280×768', '768×1280'], label="请选择输出比例",value=sd_radio_c)
                        sd_user_source_v = gr.Checkbox(label='使用原声(多国语言暂弃)', value=sd_user_source_v_c)
                        sd_prompt_txt = gr.Textbox(label="sd提示词",lines=5,max_lines = 5,value=sd_prompt_txt_c) 
                second_checkBox = gr.Checkbox(label='开启二次创作', value=second_checkBox_c)
                with gr.Column(visible = second_checkBox_c) as second_row:
                    use_gpt = gr.Checkbox(label='开启GPT润色', value=use_gpt_c)
                    prompt_txt = gr.Textbox(label="提示词",lines=5,max_lines = 5,value=prompt_txt_c,visible=use_gpt_c)  
                    
                    with gr.Row(visible = True):
                        add_bg_sound = gr.Checkbox(label='添加背景音乐', value=add_bg_sound_c)
                        add_mark = gr.Checkbox(label='添加水印', value=add_mark_c)
                        add_srt = gr.Checkbox(label='添加字幕', value=add_srt_c)
                    with gr.Row(visible = True):
                        add_hear_bottom = gr.Checkbox(label='添加头尾', value=add_hear_bottom_c)
                        force_v = gr.Checkbox(label='强制横屏', value=force_v_c)
                    with gr.Row(visible = True):
                        del_hear = gr.Textbox(label="删除开头(秒):",lines=1,max_lines = 1,value =del_hear_c ) 
                        del_bottom = gr.Textbox(label="删除结尾(秒):",lines=1,max_lines = 1,value = del_bottom_c) 
                    with gr.Row(visible = True):   
                        cut_width = gr.Slider(0.2, 1, value=1, label="保留视频宽%", info="选择0.2~1(从中间开始计算)")
                        cut_height = gr.Slider(0.2, 1, value=1, label="保留视频高%", info="选择0.2~1(从顶部开始计算)")
                with gr.Row(visible = True):
                    save_button = gr.Button(label="保存配置", value="保存配置",visible = True)   
                    del_video_button = gr.Button(label="删除二创", value="删除二创")               
                run_button = gr.Button(label="启动", value="启动")        
            with gr.Tab(label='语言设置'):
                voice_radio = gr.Radio(
                        ['男', '女'], label="请选择语言",value=voice_radio_c
                    )
                with gr.Row(visible = True) as male_row:
                    Male_select = gr.CheckboxGroup(getConryByGender("Male"),label="多选",value=Male_select_c)
                with gr.Row(visible = False) as Female_row:    
                    Female_select = gr.CheckboxGroup(getConryByGender("Female"),label="多选",value=Female_select_c)  
                    
    # 事件处理
    ctrl = [video_list,        #视频列表
            voice_radio,       #语言选择
            Male_select,       #男语言
            Female_select,     #女语言
            second_checkBox,   #开启二次创作
            use_gpt,           #开始GPT润色
            use_sd,            #开启SD创作
            prompt_txt,        #提示词
            add_bg_sound,      #添加背景
            add_mark,          #添加水印
            add_srt,           #添加字幕
            add_hear_bottom,   #添加头尾
            force_v,           #强制横屏
            del_hear,          #删除头
            del_bottom,        #删除尾
            sd_radio,          #sd视频输出比例
            sd_prompt_txt,      #sd提示词 
            cut_width,          #裁剪视频保留宽
            cut_height,          #裁剪视频保留高
            sd_user_source_v    #sd使用原声音
            ]
    voice_radio.change(update_checkbox_visibility, inputs=[voice_radio],outputs=[male_row,Female_row])
    use_sd.change(update_sd_checkbox, inputs=[use_sd],outputs=[sd_row])
    second_checkBox.change(open_second_fn, inputs=[second_checkBox], outputs=[second_row])
    use_gpt.change(use_gpt_fn, inputs=[use_gpt],outputs=[prompt_txt])  
    save_button.click(fn=save_clicked,inputs=ctrl)
    del_video_button.click(fn=del_video_clicked)
    run_button.click(fn=generate_clicked,inputs=ctrl) 
    #无用公共事件
    add_bg_sound.change(use_changed, inputs=[add_bg_sound])
    add_mark.change(use_changed, inputs=[add_mark])
    add_srt.change(use_changed, inputs=[add_srt])
    add_hear_bottom.change(use_changed, inputs=[add_hear_bottom])
    force_v.change(use_changed, inputs=[force_v])
    prompt_txt.change(use_changed, inputs=[prompt_txt])
    sd_prompt_txt.change(use_changed, inputs=[sd_prompt_txt])
    cut_width.change(use_changed, inputs=[cut_width])
    cut_height.change(use_changed, inputs=[cut_height])
    sd_user_source_v.change(use_changed, inputs=[sd_user_source_v])
    

# 设置回调函数
downloader.set_callback(on_download_complete)
downloader.set_all_callback(on_all_download_complete)
                        
parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=7888, help="Set the listen port.")
parser.add_argument("--share", action='store_true', help="Set whether to share on Gradio.")
parser.add_argument("--listen", type=str, default=None, metavar="IP", nargs="?", const="0.0.0.0", help="Set the listen interface.")
args = parser.parse_args()
gradio_root.launch(inbrowser=True, server_name=args.listen, server_port=args.port, share=args.share)