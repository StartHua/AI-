import threading
import concurrent.futures
import asyncio
from config.config import *
from utils.util import *
from Plugins.FreeGPT import freeGPTMgr
import time
from Plugins.Fooocus_req import fooocusMgr

class sd_task:
    def __init__(self, max_workers=5):
        self.task = {}  # 用于跟踪下载状态
        self.callback = None  # 用于存储回调函数
        self.all_callback = None  # 全部下载完成回调
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.running_threads = []

    def set_callback(self, callback):
        self.callback = callback

    def set_all_callback(self, callback):
        self.all_callback = callback

    def execute_task(self, id, tts,info,out_root,size):
        # 这里是你的下载逻辑
        # print(f"任务id {id}")
        # print(info)
        prompt = info.get('prompt')
        sound = info.get('sound')

        image_path = os.path.join(out_root,"img")
        create_dir(image_path)
        sound_path =os.path.join(out_root,"sound") 
        create_dir(sound_path)
        srt_path =os.path.join(out_root,"srt")
        create_dir(srt_path)
        video_path =os.path.join(out_root,"video") 
        create_dir(video_path)
        
        image_path =os.path.join(image_path,str(id)+".png")
        sound_path = os.path.join(sound_path,str(id)+".mp3")
        srt_path = os.path.join(srt_path,str(id)+".srt")
        video_path =os.path.join(video_path,str(id)+".mp4") 
        
        # 生成图片
        if not os.path.exists(image_path):
            fooocusMgr.call(image_path,prompt,size)
        #生成声音
        if not os.path.exists(sound_path):
            create_tts_mp3(tts,sound,sound_path) 
            
        long_time = int(get_video_length(sound_path))
        #字幕 
        if not os.path.exists(srt_path):
            sound_text = convert_chinese_punctuation_to_english(sound)
            sound_text = format_text(sound_text)
            start_time = 0
            end_time =start_time  + long_time
            print(f"{start_time//3600:02d}:{(start_time//60)%60:02d}:{start_time%60:02d},000 --> ")
            print(f"{end_time//3600:02d}:{(end_time//60)%60:02d}:{end_time%60:02d},000\n{sound_text}\n")
            
            subtitle_line = (
                f"1\n"
                f"{start_time//3600:02d}:{(start_time//60)%60:02d}:{start_time%60:02d},000 --> "
                f"{end_time//3600:02d}:{(end_time//60)%60:02d}:{end_time%60:02d},000\n{sound_text}\n"
            )
            with open(srt_path, "w", encoding="utf-8") as subtitle_file:
                subtitle_file.write(subtitle_line)  
        #单个视频
        if not os.path.exists(video_path):
            # 删除盘符  
            index = srt_path.find(":")
            if index != -1:
                srt_path = srt_path.split(":")[1]
            srt_path = srt_path.replace("\\","/")
            create_video_with_audio_and_subtitles(image_path, sound_path, srt_path, video_path, long_time)       
                
        self.task[id] = True
        if self.callback:
            self.callback(id, info)
        self.running_threads.remove(threading.current_thread())
    

    def task_in_thread(self, id,tts, info,out_root,size):
        if not self.executor._shutdown:  # 检查线程池是否已关闭
            thread = self.executor.submit(self.execute_task, id,tts, info,out_root,size)
            self.running_threads.append(thread)
        else:
            print("已经启动@")      

    def stop_all_threads(self):
        for thread in self.running_threads:
            thread.cancel()
        self.running_threads = []

    # 提示词,输出文案语言,tts，数据本地地址（视频，音频，txt）,输出路径，图片分辨率：1280×768 ，768×1280
    def start_task(self, prompt,country,tts,file_path, out_root,size):
        if os.path.exists(file_path):
            print(file_path)
            # 完善提示词
            prompt = prompt + SD_PROMPT(country)
            # 查看本地是否存在sd_video.json
            out_root = os.path.join(out_root,SD_DRI)
            create_dir(out_root)
            txt_file = None
            sd_file = out_root + "/" +SD_JSON 
            srt_file = out_root + "/" + SD_SRT
            if not os.path.exists(sd_file):
                if is_file(file_path,['.mp4', '.MP4','.mp3', '.MP3']):
                    print("mp4,或者mp3")
                    #转换成文本
                    # whisper_all(file_path,out_root,False,"txt")
                    file_name = get_file_name(file_path)
                    txt_file = out_root + "/" + file_name + ".txt"
                elif is_file(file_path,['.txt']):
                    print("文本")
                    txt_file = file_path
                else:
                    print("不支持类型@")        
                if txt_file != None and os.path.exists(txt_file):
                    with open(txt_file, 'r', encoding='utf-8') as file:
                        content = file.read()
                    # GPT转换
                    success,t2 = freeGPTMgr.call(prompt + content)
                    with open(sd_file, 'a',encoding='utf-8' ) as f: 
                        f.write(t2)
            with open(sd_file, 'r', encoding='utf-8') as f1:
                    content = f1.read()
                    content = json.loads(content)
                    task_list = content['content']
                     
            for cur in task_list:
                id = cur['id']
                self.task_in_thread(id,tts,cur,out_root,size)  

        self.executor.shutdown(wait=True)
       
        # 检查是否完成进行第二次进程为了保底
        image_path =os.path.join(out_root,"img")
        sound_path =os.path.join(out_root,"sound") 
        video_path =os.path.join(out_root,"video") 
        image_count = len(os.listdir(image_path))
        sound_count = len(os.listdir(sound_path))
        video_count = len(os.listdir(video_path))
        out_video = os.path.join(out_root,"sd_video.mp4")
        if image_count != len(task_list) or sound_count != len(task_list) or video_count != len(task_list):
            self.reset()
            time.sleep(1)
            for cur in task_list:
                id = cur['id']
                self.task_in_thread(id,tts,cur,out_root,size)  
            self.executor.shutdown(wait=True) 

        if image_count == len(task_list) and sound_count == len(task_list) and video_count == len(task_list):
            # 合成视频
            if not os.path.exists(out_video):
                items = os.listdir(video_path)
                videos = []
                for i in items:
                    v = os.path.join(video_path,i)
                    videos.append(v)
                if len(videos) > 0:
                    merge_videos(videos,out_video)    
                
            
        print("所有任务已完成！")
        if self.all_callback:
            self.all_callback(task_list)
        self.reset()

    def reset(self):
        self.stop_all_threads()
        # 重置线程池，以便可以再次提交新的下载任务
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.executor._max_workers)
        self.task = {}