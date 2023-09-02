import pysrt

# 字幕过长变成2行
def split_long_subtitles(input_file, output_file, max_length=25):
    # 读取SRT文件
    subs = pysrt.open(input_file)

    for sub in subs:
        # 获取字幕文本
        text = sub.text

        # 如果字幕长度超过max_length
        if len(text) > max_length:
            # 在中间位置添加换行符
            middle = len(text) // 2
            text = text[:middle] + '\\N' + text[middle:]

            # 更新字幕文本
            sub.text = text

    # 保存修改后的SRT文件
    subs.save(output_file, encoding='utf-8')