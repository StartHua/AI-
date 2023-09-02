from utils.ffmpeg_util import *
from utils.file_util import *
from utils.tts_util import *
from utils.whisper_util import *
from utils.time_util import *
from utils.movepy_util import *

import random
import platform
import uuid
# from utils.encryption_util import *

def random_file(path):
    file_list = os.listdir(path) 
    random_file = random.choice(file_list)
    return os.path.join(path, random_file)


def remove_punctuation(input_string):
    cleaned_string = re.sub(r'[^\w\s]', '', input_string)
    return cleaned_string

    # 解析抖音分享口令中的链接并返回列表/Parse the link in the Douyin share command and return a list
def find_url(string: str) -> list:
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    return url


def get_machine_code():
    command = "wmic csproduct get uuid"  # 要运行的命令
    output = subprocess.check_output(command, shell=True).decode('utf-8')  # 运行命令并获取输出
    lines = output.strip().split('\n')  # 拆分输出为行

    if len(lines) > 1:
        machine_uuid = lines[1].strip()  # 获取 UUID 值
        return str(machine_uuid)
    else:
        return None

# 字符串转数字
def validate_numeric_input(input_text):
    try:
        return float(input_text)
    except ValueError:
        return None

# 中文标点替换成英文标点
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
    converted_text =converted_text.replace(" ","")
    return converted_text.strip()    

def format_text(text):
    # 使用正则表达式将句子分割出来
    sentences = re.split(r'(?<=[.!?])', text)
    
    # 使用NLTK库的句子分割工具进行分割
    # sentences = sent_tokenize(text)
    
    # 去除空白句子
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # 在句子结束时添加换行符，并合并成格式化的文本
    formatted_text = '\n'.join(sentences)
    return formatted_text

# 检查是不是mp4
def is_file(file_path,allowed_extensions = ['.mp4', '.MP4']):
    # 获取文件的扩展名
    file_extension = file_path[file_path.rfind('.'):].lower()

    # 检查扩展名是否在允许的列表中
    if file_extension in allowed_extensions:
        return True
    else:
        return False

def get_file_name(filePath,with_ext = False):
    if not os.path.exists(filePath):
        return None 
    # 使用os.path.basename()获取文件名
    file_name = os.path.basename(filePath)
    if with_ext:
        return file_name
    file_name_without_extension = os.path.splitext(file_name)[0]
    # print("不包括扩展名的文件名:", file_name_without_extension)
    return file_name_without_extension
