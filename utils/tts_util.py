import re
import os

# 中文标点替换成英文标点
def convert_chinese_punctuation_to_english_tts(text):
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


def create_tts_mp3(voice: str, content: str, outPath: str):
    content = convert_chinese_punctuation_to_english_tts(content)
    print(content)
    script = f"edge-tts --voice  {voice} --text  {content} --write-media  {outPath}"
    os.system(script)

def create_tts_mp3_by_file(voice: str,file: str,outPath: str):
    script = f"edge-tts --voice {voice} --rate=+2%  -f  {file} --write-media {outPath}"
    # script = f"edge-tts --voice {voice} -f  {file} --write-media {outPath}"
    os.system(script)    
