import torch
import os
import g4f
from config.config import *
import re
from googletrans import Translator
from Plugins.FreeGPT import freeGPTMgr
import whisper

# whisper_model = whisper.load_model(MODE_PATH+"/" + WHISPER_MODEL)
# print()
translator = Translator()

# translate==True 统一转成en
def whisper_all(path, out,  translate: bool = False,format_txt: str = "all",threads: int = 8):
    if translate ==False:
        if torch.cuda.is_available() == True:
            WhisperScript = 'Whisper ' + path + \
                ' --model ' + WHISPER_MODEL + ' --model_dir ' + MODE_PATH + \
                ' --output_format ' + format_txt + ' --device cuda --threads ' + str(threads) +' --output_dir ' + out
        else:
            WhisperScript = 'Whisper ' + path + \
                ' --model ' + WHISPER_MODEL + ' --model_dir ' + MODE_PATH + \
                ' --output_format ' + format_txt + ' --output_dir ' + out
                
    else:
        if torch.cuda.is_available() == True:
            WhisperScript = 'Whisper ' + path + \
                ' --model ' + WHISPER_MODEL + ' --model_dir ' + MODE_PATH + \
                ' --output_format ' + format_txt + ' --task translate ' + ' --device cuda --threads ' + str(threads) +' --output_dir ' + out
        else:
            WhisperScript = 'Whisper ' + path + \
                ' --model ' + WHISPER_MODEL + ' --model_dir ' + MODE_PATH + \
                ' --output_format ' + format_txt + ' --task translate ' +  ' --output_dir ' + out 
    os.system(WhisperScript)

# def whisper_to_str(content):
#     return whisper_model.transcribe(content)
    

# https://github.com/LibreTranslate/LibreTranslate 备用翻译
# def google_trans_file(source:str,save:str,toLan: str):
#     if not os.path.exists(source):
#             return None
#     content = ""  
#     with open(source, 'r', encoding='utf-8') as file:
#             content = file.read() 
#     try:
#         t = translator.translate(content, dest="zh-CN")
#         with open(save, 'a', encoding='utf-8') as f:
#             # 如果是字幕文件不进行处理
#             s = t.text
#             if not source.endswith(".srt"):                
#                 s = convert_chinese_punctuation_to_english(t.text)
#             f.write(s)
#         return s 
    
#     except Exception  as ce:
#         print("google_trans 发生错误使用gpt翻译:", ce)
#         prompt = "使用"+toLan+"语言翻译以下内容,要求之返回翻译好的内容不需要添加任何东西:"+content
#         success,t2 = freeGPTMgr.call(prompt)
#         # 统一处理下
#         with open(save, 'a', encoding='utf-8') as f:
#             s1 = t2
#             if not source.endswith(".srt"):   
#                 s1 = convert_chinese_punctuation_to_english(t2)
#             f.write(s1)
#         return s1

def trans_language_By_GTP(source:str,save:str,toLan: str):
    if not os.path.exists(source):
        return None
    content = ""  
    with open(source, 'r', encoding='utf-8') as file:
            content = file.read() 
    prompt = "使用"+toLan+"语言翻译以下内容,要求之返回翻译好的内容不需要添加任何东西:"+content
    success,t2 = freeGPTMgr.call(prompt)
    # 统一处理下
    with open(save, 'a', encoding='utf-8') as f:
        s1 = t2
        if not source.endswith(".srt"):   
            s1 = convert_chinese_punctuation_to_english(t2)
            f.write(s1)
    return s1

def convert_chinese_punctuation_to_english(text):
    punctuation_mapping = {
        "，": ",",
        "。": ".",
        "！": "!",
        "？": "?",
        "；": ";",
        "“": "\"",
        "”": "\"",
        "‘": "'",
        "’": "'",
        "（": "(",
        "）": ")",
        "【": "[",
        "】": "]",
        "『": "[",
        "』": "]",
        "《": "<",
        "》": ">",
    }

    converted_text = text
    for chinese_punct, english_punct in punctuation_mapping.items():
        converted_text = converted_text.replace(chinese_punct, english_punct)
    
    converted_text = re.sub(r'\s+', ' ', converted_text)
    return converted_text.strip()

def google_trans(source: str,toLan: str):
    t = translator.translate(source, dest=toLan)
    s1 = convert_chinese_punctuation_to_english(t.text)
    return s1

# def create():
# # 字幕文件
#             if not os.path.exists(srt_file):
#                 subtitle_lines = []
#                 current_time = 0
#                 index = 1
#                 for item in task_list:
#                     sound_text = item["sound"]
#                     start_time = current_time
#                     end_time =start_time  + (int)(validate_numeric_input(item["long_time"])/2)
                    
#                     subtitle_line = (
#                         f"{index}\n"
#                         f"{start_time//3600:02d}:{(start_time//60)%60:02d}:{start_time%60:02d} --> "
#                         f"{end_time//3600:02d}:{(end_time//60)%60:02d}:{end_time%60:02d}\n{sound_text}\n"
#                     )
#                     subtitle_lines.append(subtitle_line)
                    
#                     current_time = end_time
#                     index = index + 1

#                 subtitle_content = "\n".join(subtitle_lines)

#                 with open(srt_file, "w", encoding="utf-8") as subtitle_file:
#                     subtitle_file.write(subtitle_content)    