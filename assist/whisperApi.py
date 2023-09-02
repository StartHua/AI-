# -*- coding: utf-8 -*-
from flask import Flask, request, Blueprint
from concurrent.futures import ThreadPoolExecutor
import json
import torch
import os
from config.config import *
from assist.GPT3_Sifc import sifcGPTMgr
import time
from utils.file_util import *
import re
import subprocess
import random
import shutil

whisper_api = Blueprint("whisper_api", __name__)
executor = ThreadPoolExecutor(5)


@whisper_api.route('/whisper', methods=['POST'])
def whisper():
    data = request.get_json()
    path = data["path"]
    groupDirs = os.listdir(path)

    if len(groupDirs) <= 0:
        return j_respone("成功")
    else:
        index = len(groupDirs)
        for groupId in groupDirs:
            gPath = os.path.join(path, groupId)
            mp3 = gPath + "/background_music.mp3"
            out = gPath
            format_txt = "txt"
            jsonFile = gPath + "/background_music.json"
            index = index - 1
            print(index)
            if os.path.exists(mp3) and not os.path.exists(jsonFile):
                print(gPath)
                executor.submit(run_script, mp3, out, format_txt, "en", True)
                time.sleep(30)

    return j_respone("成功")


def create_mp3(path: str, newCreate: bool):
    print(path)
    groupDirs = os.listdir(path)
    if len(groupDirs) <= 0:
        return j_respone("成功")
    else:
        for groupId in groupDirs:
            groupPath = os.path.join(path, groupId)
            gPath = os.path.join(groupPath, "mp3")
            # 创建输出文件夹
            if newCreate == True:
                delete_dir(gPath)
            create_dir(gPath)
            JsonFile = groupPath + "/" + "background_music.json"
            if os.path.exists(JsonFile):
                with open(JsonFile, 'r') as f:
                    data = json.load(f)
                    data = json.loads(data)
                for item in data:
                    title = item['title']
                    print(title)
                    content = item['content']
                    role = item['role']
                    voice = "zh-CN-YunxiNeural"
                    if role == "girl":
                        voice = "zh-CN-XiaoyiNeural"
                    title = remove_special_characters(title)
                    outPath = gPath + "/" + title + ".mp3"
                    executor.submit(run_tts_create_mp3,
                                    voice, content, outPath)
                    time.sleep(1)


def create_mp3_srt(path: str):
    print(path)
    groupDirs = os.listdir(path)
    if len(groupDirs) <= 0:
        return j_respone("成功")
    else:
        for groupId in groupDirs:
            gPath = os.path.join(path, groupId, "mp3")
            allMp3 = os.listdir(gPath)
            if len(allMp3) > 0:
                for item in allMp3:
                    if item.endswith(".mp3"):
                        mp3 = gPath + "/" + item

                        srtFile = gPath + "/" + item.replace(".mp3", ".srt")
                        out = gPath
                        format_txt = "srt"
                        print(mp3)
                        if os.path.exists(mp3) and not os.path.exists(srtFile):
                            executor.submit(run_script, mp3, out,
                                            format_txt, "Chinese", False)
                            time.sleep(4)

    return j_respone("成功")


def replace_gang(s: str):
    # s = s.replace("/","\\")
    # s = s.replace("\\","\\\\")
    return s


def combine_video(path: str, newCreate: bool):
    groupDirs = os.listdir(path)
    if len(groupDirs) <= 0:
        return j_respone("成功")
    else:
        for groupId in groupDirs:
            group_path = os.path.join(path, groupId)
            gPath = os.path.join(group_path, "mp3")
            vPath = os.path.join(group_path, "mp4")

            index = random.randint(1, 4)
            # 视频
            video_no_sound = group_path + "/no_sound.mp4"
            if not os.path.exists(video_no_sound):
                video_no_sound = VIDEO_PATH + "/" + str(index) + ".mp4"

            # 背景图
            bg_png = BG_IMAGE_PATH + "/" + str(index)+".jpg"
            # 背景音效
            bg_sound = BG_SOUND + "/" + str(index)+".mp3"

            if newCreate == True:
                delete_dir(vPath)
            print(vPath)
            create_dir(vPath)
            allMp3 = os.listdir(gPath)
            if len(allMp3) > 0:
                temp = 0
                for item in allMp3:
                    if item.endswith(".mp3"):
                        temp = temp + 1
                        # run_ffmpeg_combine( gPath,item,vPath,temp,path,groupId,video_no_sound,bg_sound,bg_png)
                        executor.submit(run_ffmpeg_combine, gPath, item, vPath,
                                        temp, path, groupId, video_no_sound, bg_sound, bg_png)
                        time.sleep(25)


# 把下面代码补充完整，ffmpeg 合成视频。video_no_sound 为主视频，bg_png为背景图，bg_sound为背景音效(声音低)，persion_voice人声音为主发音，srtFile字幕，mp3_len为视频长度
# 获取视频长度
def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)


def run_ffmpeg_combine(gPath, item, vPath, temp, path, groupId, video_no_sound, bg_sound, bg_png):
    # 音频
    persion_voice = gPath + "/" + item
    persion_voice = replace_gang(persion_voice)
    # 字幕
    srtFile = gPath + "/" + item.replace(".mp3", ".srt")
    destination = vPath + "/" + str(temp)+".srt"
    shutil.copy(srtFile, destination)

    basename = os.path.basename(path)
    srtFile = "./" + basename + "/" + groupId + "/mp4/" + str(temp)+".srt"

    print(srtFile)
    # 视频输出
    video_out = vPath + "/" + item.replace(".mp3", ".mp4")
    video_out_srt = vPath + "/" + item.replace(".mp3", "_.mp4")
    video_out = replace_gang(video_out)
    video_out_srt = replace_gang(video_out_srt)
    # 视频长度
    mp3_len = get_length(persion_voice)

    # 背景+视频+音乐
    script = 'ffmpeg -stream_loop 2 -i ' + video_no_sound + ' -i ' + persion_voice + ' -i ' + bg_sound + ' -loop 1 -i ' + bg_png + \
        ' -filter_complex \"[1:a]volume=1.0[a1]; [2:a]volume=0.3[a2]; [a1][a2]amix=inputs=2:duration=first:dropout_transition=2; [3:v]scale=1280:720[bg]; [bg][0:v]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2\" -acodec aac -t ' + str(
            mp3_len) + " " + video_out
    os.system(script)
    # 添加字幕
    command = ['ffmpeg', '-i', video_out, '-vf', 'subtitles=' +
               srtFile + ':force_style=\'FontSize=24\'', video_out_srt]
    subprocess.run(command, check=True)
    delete_file(destination)
    delete_file(video_out)

# 移除特殊字符


def remove_special_characters(s):
    # s= re.sub('[^\w\s\u4e00-\u9fff]+', '', string)
    s = re.sub('[!?？！]', '.', s)
    s = s.replace(",,", ",")
    s = s.replace("..", ".")
    s = s.replace("，", ",")
    return s.replace(" ", "")


def run_tts_create_mp3(voice: str, content: str, outPath: str):
    content = remove_special_characters(content)
    content = "\"" + content + "\""
    script = "edge-tts --voice " + voice + " --rate=-2%  --text " + \
        content + " --write-media " + outPath
    # script = "edge-tts --voice "+ voice +" --text " + content + " --write-media "  + outPath
    print("==========start=======")
    print(script)
    print("==========end=======")
    os.system(script)


def run_script(path, out, format_txt, language, createJson):
    file_name_with_extension = os.path.basename(path)

    file_name, file_extension = os.path.splitext(file_name_with_extension)

    # 生成字幕
    txtPath = out + "/" + file_name+"."+format_txt
    if not os.path.exists(txtPath):
        if torch.cuda.is_available() == True:
            WhisperScript = 'Whisper ' + path + \
                ' --model ' + "medium" + ' --model_dir ' + MODE_PATH + \
                ' --language ' + language + \
                ' --output_format ' + format_txt + ' --device cuda --output_dir ' + out
        else:
            WhisperScript = 'Whisper ' + path + \
                ' --model ' + "medium" + ' --model_dir ' + MODE_PATH + \
                ' --language ' + language + \
                ' --output_format ' + format_txt + ' --output_dir ' + out
        os.system(WhisperScript)

    if createJson == True:
        with open(txtPath, 'r') as file:
            content = file.read()
            # 请求gpt
            temp = '''
            请模仿以下的TikTok视频脚本文案，重新写出3个新的脚本文案,这个3个脚本内容不要相同，争议点不同，背景不一样，结局不一样，主要内容方向是女性情感故事，要求是第一句话需要比较有争议的，能够引发观众持续观看和评论，第一句作为标题,丰富更多细节，让段落更加具体。文案内容请用中文写出来。判断第一人称role可选择man,girl,输出格式json：[{title:"",content:"",role:""}]参考文案：
            '''
            temp = temp + content

        t1, t2 = sifcGPTMgr.call(temp)
        jsonPath = out + "/" + file_name+"."+"json"
        if t1 == False:
            print("失败！")
        else:
            with open(jsonPath, 'w') as file:
                # 使用json.dump()函数将数据写入文件
                json.dump(t2, file)
        print("生成json文件！")


def j_respone(data, msg="成功！", code=200):
    respone = {}
    respone["code"] = code
    respone["msg"] = msg
    respone["data"] = data
    return json.dumps(respone, indent=4, ensure_ascii=False)
