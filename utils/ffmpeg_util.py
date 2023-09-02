import os
import subprocess
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy import editor
import ffmpeg
# 分离视频：无声音
def split_video_mute(voidePath, outPath):
    script = 'ffmpeg -i ' + voidePath + " -an -vcodec copy " + outPath
    os.system(script)


# 分离视频:声音mp3
def split_sound(voidePath, outPath):
    script = 'ffmpeg -i ' + voidePath + ' -map 0:a:0 ' + outPath
    os.system(script)

# 加上图片
def add_mark_to_video(input_video, mark_image, output_video):
    script = (
        f'ffmpeg -i {input_video} -i {mark_image} '
        f'-filter_complex "[0:v][1:v]overlay=W-w-10:H-h-10[out]" '
        f'-map "[out]" -map 0:a -c:v libx264 -c:a copy {output_video}'
    )
    os.system(script)

def combine_video_with_bg(source_file, bg_image,lenOut:int, output_file, width=1280, height=720):
    script = (
        f'ffmpeg -i {source_file} -loop 1 -i {bg_image} '
        f'-filter_complex "[1]scale={width}:{height}[bg]; [bg][0:v]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[video_with_overlay]" '
        f'-map "[video_with_overlay]" -c:v libx264 -t {str(lenOut)} {output_file}'
    )
    print(script)
    subprocess.run(script, shell=True)

    
# 合并字幕
def combine_srt(video_path:str,srtFile:str,out_path:str):
    # 添加字幕
    command = ['ffmpeg', '-i', video_path, '-vf', 'subtitles=' +
               srtFile + ':force_style=\'FontSize=16\'', out_path]
    subprocess.run(command, check=True)


# 获取视频长度
def get_video_length(filePath):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filePath],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)

   

def combine_video_with_bg_sound(mp4, mp3, mp3_len, out_file, bg_sound, width=1280, height=720):
    script = (
        f'ffmpeg -stream_loop 2 -i "{mp4}" -i "{mp3}" -i "{bg_sound}" '
        f'-filter_complex "[1:a]volume=1.0[a1]; [2:a]volume=0.3[a2]; '
        f'[a1][a2]amix=inputs=2:duration=longest:dropout_transition=2[a_mix]; '
        f'[0:v]fps=30,scale={width}:{height}[bg_overlay]" '
        f'-map "[a_mix]" -map "[bg_overlay]" -c:a aac -t {str(mp3_len)} "{out_file}"'
    )
    print(script)
    os.system(script)
    

def combine_video_source(mp4, mp3, mp3_len, out_file, width=1280, height=720):
    script = (
        f'ffmpeg -stream_loop 2 -i {mp4} -i {mp3} '
        f'-filter_complex "[1:a]volume=1.0[a1]; '
        f'[a1]amix=inputs=1:duration=first:dropout_transition=2; '
        f'[0:v]fps=30,scale={width}:{height}[scaled]" '  # 指定视频的宽度和高度
        f'-map "[scaled]" -acodec aac -t {str(mp3_len)} {out_file}'
    )
    print(script)
    os.system(script)
 
 
# 确保视频分辨率统一
def change_video_sacle(path,out,w = 1280,h=768):
    
    f1 = (
        f'ffmpeg -i {path} -vf "scale={w}:{h}" {out}'
    )
    subprocess.run(f1, shell=True)

# 裁剪视频区域（从中间开始）
def crop_video(input_file, output_file,widthScale = 1,heightScale = 1):
    # 获取视频的元信息
    probe = ffmpeg.probe(input_file)
    video_info = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    width = int(video_info['width'])
    height = int(video_info['height'])

    # 计算裁剪参数
    new_width = int(width * widthScale)
    new_height = int(height * heightScale)
    x = (width - new_width) // 2
    y = 0

    # 裁剪视频
    (
        ffmpeg
        .input(input_file)
        .output(output_file, vf='crop={}:{}:{}:{}'.format(new_width, new_height, x, y))
        .run()
    )



def create_video_with_audio_and_subtitles(image_path, audio_path, subtitles_path, output_path, duration):
    cmd = [
        'ffmpeg',
        '-loop', '1',
        '-i', image_path,
        '-i', audio_path,
        '-t', str(duration),
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-vf', f"subtitles='{subtitles_path}'",
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_path
    ]

    try:
        subprocess.run(cmd, check=True)
        print("视频合成完成！")
    except subprocess.CalledProcessError as e:
        print("视频合成失败：", e)

def transcode_to_mp4(input_path, output_path):
    try:
        # Construct FFmpeg command for transcoding to MP4
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'libx264', '-c:a', 'aac',
            '-strict', 'experimental',
            '-y',  # Overwrite output file without asking
            output_path
        ]
        
        # Run FFmpeg command
        subprocess.run(ffmpeg_cmd, check=True)
        print("Transcoding to MP4 successful!")
    except subprocess.CalledProcessError as e:
        print("Error transcoding to MP4:", e)        