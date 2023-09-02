import os
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

UP_PROJECT_PATH = os.path.join(PROJECT_PATH, "Py")


BG = os.path.join(UP_PROJECT_PATH, "assets")

BG_IMAGE_PATH = os.path.join(BG, "bg_image")

VIDEO_PATH = os.path.join(BG, "video")

BG_SOUND = os.path.join(BG, "bg_sound")

HEAD_L_VIDEIO =  os.path.join(BG, "head/head_L")  #开头视频横屏
HEAD_V_VIDEIO =  os.path.join(BG, "head/head_V")  #开头视频横屏

BOTTTOM_L_VIDEIO = os.path.join(BG, "bottom/bottom_L")  #结尾视频
BOTTTOM_V_VIDEIO = os.path.join(BG, "bottom/bottom_V")  #结尾视频

MARK_IMAGE =os.path.join(BG, "mark")  #左下角mark

File_Name_Prefix = ""

Download_Path = "./download"

# 没有声音的视频
MUTE_VIDEO = "mute.mp4"

SOUND_FILE_NAME = "sound"
# 声音
SOUND_MP3 = SOUND_FILE_NAME + ".mp3"

# 字幕
SOUND_SRT = SOUND_FILE_NAME + ".srt"

#  字幕txt
SOUND_TXT = SOUND_FILE_NAME + ".txt"

# 新GPT润色生成文件
EMBELLISH_STORY = "embellish.txt"

# Whisper模型
WHISPER_MODEL = "large-v2"
MODE_PATH = os.path.join(UP_PROJECT_PATH, "model")


CHINESE_FONT = os.path.join(UP_PROJECT_PATH, "assets","font","chinese_font.ttf")

TITLE = "AI视频创作"

COM_PROMPT = '请模仿以下脚本文案，重新写出新的脚本文案,争议点不同，要求是第一句话需要比较有争议的，能够引发观众持续观看和评论,丰富更多细节，让段落更加具体,参考文案：'

SD_DRI = "SD_DIR" 
 
def SD_PROMPT(language):
    return f"""
            请根据给定的文案，创作一个新的视频文案。文案应以第一人称进行演讲，内容积极。文案长度大于1000字左右。

            输出的文案格式应为JSON，{{"title":"","content":[{{"id":0,"prompt":"","sound":""}}]}}包含以下元素：
            - title：视频标题，应能引发用户的评论和讨论，最好使用疑问句。
            - content：包含多个对象，每个对象包含以下元素：
            - id：镜头ID，应为从1000开始的阿拉伯数字。
            - sound：演讲语音内容，内容必须是{language}语言，句子长度不能大于80字符。
            - prompt：提示词，要求如下：
                - 使用逗号分隔。
                - 第一个提示词必须是{language}对应的英文国家名称。
                - 本提示词是对sound演讲内容提出，所以必须包含详细的场景提示，包括语句中提到的物体、植物等。
                - 如果存在人物，必须包含人物行为的提示词，且应跟在该人物后面。
                - 所有提示词都必须是英文。
            
            每个镜头的时长也应明确标注，每个镜头演讲不能太长小于80个字符，以确保视频的流畅性和连贯性。请注意，返回的内容只能是json数据。
"""

SD_JSON = "sd_video.json"
SD_SRT = "sd_srt.srt"