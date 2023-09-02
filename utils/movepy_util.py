from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.fx.resize import resize

from PIL import Image
import numpy as np

def get_video_size(video_path:str):
    video_clip = VideoFileClip(video_path)
    # 获取宽度和高度
    return video_clip.w, video_clip.h
# 是否是横屏
def is_video_L(video_path:str):
    video_clip = VideoFileClip(video_path)
    # 获取宽度和高度
    return video_clip.w > video_clip.h

# 合并一个视频以person_audio_path声音长度为主
def merge_and_adjust_videos(main_video_path, person_audio_path, output_path, bg_sound_path=None):
    main_video = VideoFileClip(main_video_path)
    person_audio = AudioFileClip(person_audio_path)
    
    audio_duration = person_audio.duration
    video_duration = main_video.duration
    
    # 计算需要重复播放视频的次数
    repetitions = int(audio_duration / video_duration)
    remainder = audio_duration % video_duration
    
    # 循环播放主视频，直到填充音频长度
    main_video_repeated = main_video.fx(vfx.loop, n=repetitions).volumex(0)
    
    # 保留音频能够填充的部分，切割多余部分
    main_video_final = main_video_repeated.crossfadein(1).subclip(0, remainder).set_duration(audio_duration)
    
    # 设置主声音和视频进行合并
    main_video_final = main_video_final.set_audio(person_audio)
    
    # 添加额外的背景音效
    if bg_sound_path:
        bg_sound = AudioFileClip(bg_sound_path).volumex(0.4)
        bg_sound = bg_sound.subclip(0, audio_duration)
        main_audio = main_video_final.audio
        final_audio = CompositeAudioClip([main_audio.volumex(1.0), bg_sound])
    else:
        final_audio = main_video_final.audio
    
    # 将合并的音频应用到主视频上
    main_video_final = main_video_final.set_audio(final_audio)
    
    main_video_final.write_videofile(output_path, codec="libx264")

# 多视频合成一个
def merge_videos(input_videos, output_video):
    video_clips = []
    
    for video_path in input_videos:
        clip = VideoFileClip(video_path)
        video_clips.append(clip)
    
    final_clip = concatenate_videoclips(video_clips, method="compose")
    final_clip.write_videofile(output_video)

# 裁剪视频
def crop_video(input_path, output_path, start_cut=0, end_cut=0):
    clip = VideoFileClip(input_path).subclip(start_cut, -end_cut)
    clip.write_videofile(output_path, codec="libx264")
    
# def create_video_with_audio_and_subtitles(image_path, audio_path, subtitles_path, output_path, duration):
#     image_clip = ImageClip(image_path, duration=duration)
#     audio_clip = AudioFileClip(audio_path)
#     subtitles = SubtitlesClip(subtitles_path, fontsize=24)

#     video_clip = CompositeVideoClip([image_clip.set_audio(audio_clip), subtitles.set_duration(duration)])
#     video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
    