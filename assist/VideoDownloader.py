# 第二版本：python app.py
import threading
import time
import concurrent.futures
import re
import aiohttp
import zipfile
import asyncio
import concurrent.futures
from config.config import *
import subprocess
from utils.util import *
from config.tts_language import ttsLanguageMgr
from pytube import YouTube
from Plugins.scraper import Scraper

from assist.sd_task import sd_task

api = Scraper()

class VideoDownloader:
    def __init__(self, max_workers=5):
        self.downloaded = {}  # 用于跟踪视频下载状态
        self.callback = None  # 用于存储回调函数
        self.all_callback = None #全部下载完成回调
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.running_threads = []
    
    # 这种每个视频下载回调
    def set_callback(self, callback):
        self.callback = callback
    # 全部视频下载完成
    def set_all_callback(self,callback):
        self.all_callback = callback    
    
    # 下载youtobe
    def download_youtobe(self,url,args):
        p = r"v=([a-zA-Z0-9_-]+)"
        match = re.search(p, url)
        if not match:
            print("Video ID not found in the URL.")
            return
        aweme_id = match.group(1)
        root_path,fileName,video_path = self.get_video_info(aweme_id)
        if not os.path.exists(video_path):
            yt =YouTube(url)
            # 篩選 progressive 類型的 MP4 影片格式
            progMP4 = yt.streams.filter(progressive=True, file_extension='mp4')
            targetMP4 = progMP4.order_by('resolution').desc().first()
            out_file = targetMP4.download(root_path)
            os.rename(out_file, video_path)
        self.create_video_second(aweme_id,args)
        
            
    # 下载bilibili 
    def download_bilibili(self,url,args):
        match = re.search(r"video/(.*?)/", url)
        if match:
            aweme_id = match.group(1)
        if not aweme_id:  
            print("Video ID not found in the URL.")
            return
        root_path,fileName,video_path = self.get_video_info(aweme_id)
        if not os.path.exists(video_path): 
            command = f'you-get -o {root_path} {url}'
            subprocess.run(command, shell=True)
            # 遍历文件夹中的所有文件
            dirs = os.listdir(root_path)
            for file in dirs:
                if file.endswith(".cmt.xml"):
                    file_name_without_extension = file.replace(".cmt.xml", "")
                    source_video = os.path.join(root_path, file_name_without_extension+".mp4")
                    os.rename(source_video, video_path)
                    os.remove(os.path.join(root_path,file))
        #对视频进一步处理
        self.create_video_second(aweme_id=aweme_id,args=args)
    
    #下载tiktok,抖音
    async def download_tiktok(self,url,args):
        print("下载tiktok,抖音")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        data = await api.hybrid_parsing(url)
        url_type = data.get('type')
        platform = data.get('platform')
        aweme_id = data.get('aweme_id')
        root_path,fileName,video_path = self.get_video_info(aweme_id)
        if url_type == 'video':
            url = data.get('video_data').get('nwm_video_url_HQ') if not False else data.get('video_data').get(
                    'wm_video_url_HQ')
            # 判断文件是否存在，存在就直接返回
            if not os.path.exists(video_path):
                if platform == 'douyin':
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url=url, headers=headers, allow_redirects=False) as response:
                            r = response.headers
                            cdn_url = r.get('location')
                            async with session.get(url=cdn_url) as res:
                                r = await res.content.read()
                elif platform == 'tiktok':
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url=url, headers=headers) as res:
                            r = await res.content.read()
                with open(video_path, 'wb') as f:
                    f.write(r)
            self.create_video_second(aweme_id,args)
        else:
            print("非视频@")            
    
    # 二创
    def create_video_second(self,aweme_id,args):
        second_create = args[4]
        sd_create = args[6]
        sd_prompt = args[16]
        sd_scale = args[15]
        #对视频进一步处理
        self.deal_video(aweme_id,args)  
        # 二创
        if second_create ==True:
            self.create_by_country(aweme_id=aweme_id,args=args)
        # sd创作
        if sd_create ==True:
            tts_list = self.get_languages_by_args(args)
            print(tts_list)
            return
            root_path,fileName,video_path = self.get_video_info(aweme_id)
            sd_txt = root_path +"/" + SOUND_TXT 
            sd_sound = root_path +"/" + SOUND_MP3
            if not os.path.exists(sd_txt):
                sd_txt = sd_sound 
            for item in tts_list:
                country = item["country"]
                tts = item["tts"]
                dir = root_path + "/" + country 
                create_dir(dir)
                sd = sd_task(2)
                sd.start_task(sd_prompt,
                            country,
                            tts,
                            sd_txt,
                            dir,
                            sd_scale
                            )
                            
        
    # 获取视频文件夹，文件名，mp4路径
    def get_video_info(self,aweme_id):
        dir = Download_Path + "/" + aweme_id
        # 查看目录是否存在，不存在就创建
        if not os.path.exists(dir):
            os.makedirs(dir)
        file_name = aweme_id +".mp4"   
        video_path = dir + "/" + file_name
        return dir,file_name,video_path
    
    # 获取语言列表
    def get_languages_by_args(self,args):
        voice_radio = args[1]
        select_in = []
        if voice_radio == "男":
           select_in =  args[2]
        else:
           select_in =  args[3] 
            
        selected_languages = []
        for label in select_in:   
            for language in ttsLanguageMgr.language:
                temp = f"{language['country']} ({language['cn']})"
                if label==temp:
                    selected_languages.append(language)
        return selected_languages            
    
    # 对视频进一步处理
    def deal_video(self,aweme_id,args):
        root_path,fileName,video_path = self.get_video_info(aweme_id)
        # 分离静音视频
        no_sound_video = root_path + "/" + MUTE_VIDEO
        if not os.path.exists(no_sound_video):
            split_video_mute(video_path, no_sound_video)
        # 分离mp3
        sound = root_path + "/" + SOUND_MP3
        if not os.path.exists(sound):
            split_sound(video_path, sound)
        # 统一生成英文字幕+文案
        en_srt = root_path + "/" + SOUND_SRT
        en_txt = root_path +"/" + SOUND_TXT
        if not os.path.exists(en_srt) or not os.path.exists(en_txt):
            whisper_all(sound, root_path,True)
        # GPT 润色生成新文档或者故事
        embellish_file = root_path + "/" + EMBELLISH_STORY
        embellishStory = args[5]
        prompt = args[7]
        # 默认提示词
        if not prompt or prompt == "":
           prompt = COM_PROMPT
        if embellishStory == True and not os.path.exists(embellish_file):
            with open(en_txt, 'r', encoding='utf-8') as file:
                content = file.read()
                prompt = prompt + content
                t1,t2 = freeGPTMgr.call(prompt) 
                # 中文标点
                t2 = convert_chinese_punctuation_to_english(t2)
                if t1 == False:
                    print("失败！")
                    return
                else:
                    with open(embellish_file, 'a',encoding='utf-8' ) as f: 
                        f.write(t2) 
    # 处理国家视频
    def create_by_country(self,aweme_id,args):
        # 是否开启二创
        second_checkBox_c = args[4]
        if second_checkBox_c == False:
            return
        root_path,fileName,video_path = self.get_video_info(aweme_id)
        #读表  生成字幕+文案    
        tts_list = self.get_languages_by_args(args)
        embellishStory = args[5] 
        add_srt = args[10] 
        add_bg_sound = args[8]
        add_mark = args[9]
        add_hear_bottom = args[11]
        force_v =  args[12]
        del_head = args[13]
        del_bottom = args[14]
        cut_width = args[17]
        cut_height = args[18]
        del_head = validate_numeric_input(del_head)
        if del_head == None :
            del_head = 0
        del_bottom = validate_numeric_input(del_bottom)
        if del_bottom == None :
            del_bottom = 0    
        for item in tts_list:
            # 翻译语言
            whisper = item["whisper"]
            country = item["country"]
            tts = item["tts"]
            dir = root_path + "/" + country 
            create_dir(dir)
            # 翻译txt + 生成srt
            country_txt = dir +"/" + SOUND_TXT 
            en_txt = root_path +"/" + SOUND_TXT
            # 使用新文案
            if embellishStory:
               en_txt = root_path + "/" + EMBELLISH_STORY

            if not os.path.exists(country_txt):
                trans_language_By_GTP(en_txt,country_txt,whisper)
                time.sleep(1)   
            # 创建语音文件
            out_mp3 = dir +"/" + SOUND_MP3 
            if not os.path.exists(out_mp3):
                create_tts_mp3_by_file(tts,country_txt,out_mp3)  
                time.sleep(1) 
                
            # 创建字幕文件
            country_srt = dir +"/" + SOUND_SRT
            if add_srt and not os.path.exists(country_srt):
                whisper_all(out_mp3, dir,False,"srt")
                time.sleep(1) 
                # 修改字幕长度显示
            #静音视频  
            mute_video = root_path + "/" + MUTE_VIDEO    
            # 背景音效 
            bg_sound = None 
            if add_bg_sound:
                bg_sound = random_file(BG_SOUND)            

            # 视频输出路径
            cur_video = mute_video
            cut_video = dir + "/0_cut.mp4"
            force_out = dir + "/0_force.mp4"
            cut_out = dir + "/1_cut.mp4"
            source_out = dir + "/2_sound.mp4"
            mark_vdieo = dir + "/3_mark.mp4"
            srt_mp4 =  dir + "/4_srt.mp4"
            concat_video = dir + "/5_concat.mp4"
            
            #裁剪视频高宽度 
            if cut_width != 1 or cut_height != 1 :
                if not os.path.exists(cut_video):
                    crop_video(cur_video,cut_video,cut_width,cut_height)
                cur_video = cut_video    
            
            # 视频源是否是横屏
            source_L =  is_video_L(cur_video)
            # 是否强制修改视频为横 + 本身就不是横视频 
            if force_v and not source_L :
                if not os.path.exists(force_out):
                    bg_png =  random_file(BG_IMAGE_PATH)
                    combine_video_with_bg(cur_video, bg_png,get_video_length(cur_video) ,force_out,1280, 720)
                    time.sleep(1)  
                cur_video =  force_out   
            #裁剪视频前后头多长
            if del_head > 0 or del_bottom > 0:
                if not os.path.exists(cut_out):
                    crop_video(cur_video,cut_out,del_head,del_bottom)
                cur_video  = cut_out        
            # 合成音效合成视频    
            if not os.path.exists(source_out): 
                if source_L or force_v:
                    w = 1280
                    h = 768
                else:
                    w = 768
                    h = 1280    
                mp3_len = get_video_length(out_mp3)
                if not bg_sound:
                    combine_video_source(cur_video,out_mp3,mp3_len,source_out,w ,h)
                else:
                    combine_video_with_bg_sound(cur_video,out_mp3,mp3_len,source_out,bg_sound,w ,h)  
                time.sleep(1)        
            cur_video = source_out
            # 加入mark 
            if add_mark:
                if not os.path.exists(mark_vdieo):
                    mark =  random_file(MARK_IMAGE)
                    add_mark_to_video(cur_video,mark,mark_vdieo)
                    time.sleep(1)
                cur_video = mark_vdieo  
            # 添加字幕
            if add_srt:
                if not os.path.exists(srt_mp4):
                    combine_srt(cur_video,country_srt,srt_mp4)
                cur_video = srt_mp4   
            #合并3个视频  
            if  add_hear_bottom:
                if not os.path.exists(concat_video) :
                    if  force_v or source_L:
                        HEAD_VIDEIO = HEAD_L_VIDEIO
                        BOTTTOM_VIDEIO = BOTTTOM_L_VIDEIO
                    else:
                        HEAD_VIDEIO = HEAD_V_VIDEIO
                        BOTTTOM_VIDEIO = BOTTTOM_V_VIDEIO   
                    v1= random_file(HEAD_VIDEIO)
                    v3= random_file(BOTTTOM_VIDEIO)
                    v = [v1,cur_video,v3]    
                    merge_videos(v,concat_video)
                    time.sleep(1)  
                cur_video = concat_video       
    
    
    def download_video(self, url,args):

        if "www.youtube.com" in url:
            self.download_youtobe(url,args)
        elif ("www.tiktok.com" in url) or ("www.douyin.com" in url):
            # self.download_tiktok(url,args)
            loop = asyncio.new_event_loop()  # 创建一个新的事件循环
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.download_tiktok(url, args))
            loop.close()  # 关闭新的事件循环
        else:
            self.download_bilibili(url,args)
            
        print(f"完成下载视频 {url}")
        self.downloaded[url] = True
        if self.callback:
            self.callback(url,args)
        self.running_threads.remove(threading.current_thread())
        
    def download_in_thread(self, url,args):
        if not self.executor._shutdown:  # 检查线程池是否已关闭
            thread = self.executor.submit(self.download_video, url,args)
            self.running_threads.append(thread)
        else:
            print("已经启动@")    
    
    def stop_all_threads(self):
        for thread in self.running_threads:
            thread.cancel()
        self.running_threads = []    

    def download_all(self, url_list,args):
        for url in url_list:
            self.download_in_thread(url,args)

        self.executor.shutdown(wait=True)
        print("所有视频下载任务已完成！")
        if self.all_callback != None:
            self.all_callback(args)
        self.reset()

    def reset(self):
        self.stop_all_threads()
        # 重置了线程池，以便可以再次提交新的下载任务
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.executor._max_workers)
        self.downloaded = {}
        

# 创建 VideoDownloader 实例
# downloader = VideoDownloader(max_workers=5)

# # 回调函数示例
# def on_download_complete(url):
#     print(f"视频 {url} 下载已完成！")

# def on_all_download_complete():
#     print("全部下载完成！")

# # 设置回调函数
# downloader.set_callback(on_download_complete)
# downloader.set_all_callback(on_all_download_complete)

# # 示例用法
# url_list = ["url1", "url2", "url3", "url4", "url5", "url6", "url7", "url8"]
# downloader.download_all(url_list)

# # 重置下载状态
# downloader.reset()
