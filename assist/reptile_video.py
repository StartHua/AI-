# 第一个版本基本已经废弃（python main.py） 这个版本没有sd创作
import os
import re
import time
import json
import aiohttp
import zipfile
from concurrent.futures import ThreadPoolExecutor

from fastapi.responses import ORJSONResponse, FileResponse

from Plugins.scraper import Scraper
from config.config import *
from config.tts_language import ttsLanguageMgr
from utils.util import *
import random
from pytube import YouTube
from Plugins.FreeGPT import freeGPTMgr


api = Scraper()
executor = ThreadPoolExecutor(3)


class reptile_video:
    def __init__(self) -> None:
        pass

    # url: str,                     # 抖音或者TikTok视频url
    # create: bool = True,          # 开启二次创作
    # tts_list: list = [],          # 输出字幕语音
    # embellishStory: bool = True,  # 启动gpt润色
    # prompt                        # gpt润色提示词
    async def download_file_hybrid(self,
                                   url: str,
                                   create: bool = True,
                                   tts_list: list = [],
                                   embellishStory: bool = False,
                                   prompt: str = None,
                                   add_bg_sound:bool = True,
                                   enable_top_video:bool=True,
                                   enable_mark:bool = True,
                                   add_srt:bool = True,
                                   enable_shu_video:bool = True,
                                   cut_start:int = 0,
                                   cut_end:int = 0,
                                   prefix: bool = True,
                                   watermark: bool = False):
        
        """
            ## 用途/Usage
            ### [中文]
            - 将[抖音|TikTok]链接作为参数提交至此端点，返回[视频|图片]文件下载请求。
            ### [English]
            - Submit the [Douyin|TikTok] link as a parameter to this endpoint and return the [video|picture] file download request.
            # 参数/Parameter
            - url:str -> [Douyin|TikTok] [视频|图片] 链接/ [Douyin|TikTok] [video|image] link
            - prefix: bool -> [True/False] 是否添加前缀/Whether to add a prefix
            - watermark: bool -> [True/False] 是否添加水印/Whether to add a watermark
            """
        if "www.youtube.com" in url:
            print("下载youtobe视频")
            self.downLoad_youtobe(url,create,tts_list,embellishStory,prompt,add_bg_sound,enable_top_video,enable_mark,add_srt,enable_shu_video,cut_start,cut_end,prefix)
            return    

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        data = await api.hybrid_parsing(url)
        if data is None:
            return ORJSONResponse(data)
        else:
            url_type = data.get('type')
            platform = data.get('platform')
            aweme_id = data.get('aweme_id')
            file_name_prefix = File_Name_Prefix if prefix else ''
            root_path = Download_Path + "/" + aweme_id
            # 查看目录是否存在，不存在就创建
            if not os.path.exists(root_path):
                os.makedirs(root_path)
            if url_type == 'video':
                file_name = file_name_prefix + platform + '_' + aweme_id + \
                    '.mp4' if not watermark else file_name_prefix + \
                    platform + '_' + aweme_id + '_watermark' + '.mp4'
                url = data.get('video_data').get('nwm_video_url_HQ') if not watermark else data.get('video_data').get(
                    'wm_video_url_HQ')

                file_path = root_path + "/" + file_name
                print('文件路径: ', file_path)
               
                # 判断文件是否存在，存在就直接返回
                if not os.path.exists(file_path):
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
                    with open(file_path, 'wb') as f:
                        f.write(r)

                    # 生产素材
                if create == True:
                    self.create_asset(root_path,file_path,tts_list,embellishStory,prompt,add_bg_sound,enable_top_video,enable_mark,add_srt,enable_shu_video,cut_start,cut_end)
                    

                return FileResponse(path=file_path, media_type='video/mp4', filename=file_name)
            elif url_type == 'image':
                url = data.get('image_data').get('no_watermark_image_list') if not watermark else data.get(
                    'image_data').get('watermark_image_list')
                zip_file_name = file_name_prefix + platform + '_' + aweme_id + \
                    '_images.zip' if not watermark else file_name_prefix + \
                    platform + '_' + aweme_id + '_images_watermark.zip'
                zip_file_path = root_path + "/" + zip_file_name
                # 判断文件是否存在，存在就直接返回、
                if os.path.exists(zip_file_path):
                    print('文件已存在，直接返回')
                    return FileResponse(path=zip_file_path, media_type='zip', filename=zip_file_name)
                file_path_list = []
                for i in url:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url=i, headers=headers) as res:
                            content_type = res.headers.get('content-type')
                            file_format = content_type.split('/')[1]
                            r = await res.content.read()
                    index = int(url.index(i))
                    file_name = file_name_prefix + platform + '_' + aweme_id + '_' + str(
                        index + 1) + '.' + file_format if not watermark else \
                        file_name_prefix + platform + '_' + aweme_id + '_' + str(
                            index + 1) + '_watermark' + '.' + file_format
                    file_path = root_path + "/" + file_name
                    file_path_list.append(file_path)
                    with open(file_path, 'wb') as f:
                        f.write(r)
                    if len(url) == len(file_path_list):
                        zip_file = zipfile.ZipFile(zip_file_path, 'w')
                        for f in file_path_list:
                            zip_file.write(os.path.join(f), f,
                                           zipfile.ZIP_DEFLATED)
                        zip_file.close()
                        return FileResponse(path=zip_file_path, media_type='zip', filename=zip_file_name)
            else:
                return ORJSONResponse(data)

    # 批量下载
    async def batch_download_file(self, url_list: str,
                                  create: bool = True,
                                  tts_list: list = [],
                                  embellishStory: bool = False,
                                  prompt: str = None,
                                  add_bg_sound:bool = True,
                                  enable_top_video:bool=True,
                                  enable_mark:bool = True,
                                  add_srt:bool = True,
                                  enable_shu_video:bool = True,
                                  cut_start:int = 0,
                                  cut_end:int = 0,
                                  prefix: bool = True,
                                  souce_video_watermark: bool = False):
        """
        批量下载文件端点/Batch download file endpoint
        未完工/Unfinished
        """
        if prompt == "":
            prompt = None
        print('url_list: ', url_list)
        if len(url_list) < 0:
            print("没有视频需要下载")
        index = len(url_list)
        for url in url_list:
            print("执行下载:" + str(index))
            index = index - 1
            # 解析
            await self.download_file_hybrid(url, create, tts_list, embellishStory, prompt,add_bg_sound,enable_top_video,enable_mark,add_srt,enable_shu_video, cut_start,cut_end,prefix, souce_video_watermark)
        return ORJSONResponse({"status": "success",
                               "message": "成功下载@"})

    # 爬虫youtobe
    def downLoad_youtobe(self,
                                   url: str,
                                   create: bool = True,
                                   tts_list: list = [],
                                   embellishStory: bool = False,
                                   prompt: str = None,
                                   add_bg_sound:bool = True,
                                   enable_top_video:bool=True,
                                   enable_mark:bool = True,
                                   add_srt:bool = True,
                                   enable_shu_video:bool = True,#使用原视频分辨率
                                   cut_start:int = 0,
                                   cut_end:int = 0,
                                   prefix: bool = True,
                                   watermark: bool = False):
        p = r"v=([a-zA-Z0-9_-]+)"
        match = re.search(p, url)
        if not match:
            print("Video ID not found in the URL.")
            return
        aweme_id = match.group(1)
        print("视频id:" + aweme_id)
        root_path = Download_Path + "/" + aweme_id
        # 查看目录是否存在，不存在就创建
        if not os.path.exists(root_path):
            os.makedirs(root_path)
        file_name = aweme_id +".mp4"   
        file_path = root_path + "/" + file_name
        print('文件路径: ', file_path)
        if not os.path.exists(file_path):
            yt =YouTube(url)
            # 篩選 progressive 類型的 MP4 影片格式
            progMP4 = yt.streams.filter(progressive=True, file_extension='mp4')
            targetMP4 = progMP4.order_by('resolution').desc().first()
            out_file = targetMP4.download(root_path)
            os.rename(out_file, file_path)
      
        if create == True:
            self.create_asset(root_path,file_path,tts_list,embellishStory,prompt,add_bg_sound,enable_top_video,enable_mark,add_srt,enable_shu_video,cut_start,cut_end)

    def create_asset(self,root_path:str,
                     video_path:str,
                     tts_list: list= [],
                     embellishStory:bool = False,
                     prompt: str = None,
                     add_bg_sound:bool = True,
                     enable_top_video:bool=True,
                     enable_mark:bool = True,
                     add_srt:bool = True,
                     enable_shu_video:bool = True,
                     cut_start:int = 0,
                     cut_end:int = 0,
                     ):
        
        if not prompt:
            prompt = '请模仿以下脚本文案，重新写出新的脚本文案,争议点不同，要求是第一句话需要比较有争议的，能够引发观众持续观看和评论,丰富更多细节，让段落更加具体,参考文案：'
        
        # 分离静音视频
        no_sound_video = root_path + "/" + MUTE_VIDEO
        if not os.path.exists(no_sound_video):
            split_video_mute(video_path, no_sound_video)
        # 分离mp3
        sound = root_path + "/" + SOUND_MP3
        if not os.path.exists(sound):
            split_sound(video_path, sound)
        #读表  生成字幕
        if len(tts_list)<=0:
            tts_list = ttsLanguageMgr.language
        for item in tts_list:
            # 翻译语言
            whisper = item["whisper"]
            country = item["country"]
            tts = item["tts"]
           
            # 其他国家字幕
            temp = root_path + "/" +country 
            create_dir(temp)

            # 统一生成英文字幕
            en_srt = root_path + "/" + SOUND_SRT
            en_txt = root_path +"/" + SOUND_TXT
            if not os.path.exists(en_srt) or not os.path.exists(en_txt):
                whisper_all(sound, root_path,True)
               
            # GPT 润色生成新文档或者故事
            embellish_file = root_path + "/" + EMBELLISH_STORY
            if embellishStory == True and os.path.exists(en_txt) and not os.path.exists(embellish_file):
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
            # 设置润色后翻译文件         
            if embellishStory == True:
                en_txt = embellish_file
       
            # 翻译txt
            country_txt = temp +"/" + SOUND_TXT 
            if not os.path.exists(country_txt):
                trans_language_By_GTP(en_txt,country_txt,whisper)
                   
                
            # 翻译srt:非润色,润色后面重新mp3生成
            country_srt = temp +"/" + SOUND_SRT
            if not embellishStory and not os.path.exists(country_srt):
                trans_language_By_GTP(en_srt,country_srt,whisper)   
            #执行创建合成
            # self.run_script(root_path,country, tts,whisper,add_bg_sound,enable_top_video,enable_mark,enable_shu_video)
            executor.submit(self.run_script,root_path,country, tts,whisper,add_bg_sound,enable_top_video,enable_mark,add_srt,enable_shu_video,cut_start,cut_end)
            time.sleep(2) 
           

    def run_script(self,root_path,country,tts,whisper,add_bg_sound,enable_top_video,enable_mark,add_srt,enable_shu_video,cut_start:int = 0,
                     cut_end:int = 0,):
        #生成Mp3文件
        path = root_path + "/" + country
        out_mp3 = path +"/" + SOUND_MP3 
        mp3_txt_file = path +"/" + SOUND_TXT

        # 创建多国语言mp3
        if not os.path.exists(out_mp3):
            create_tts_mp3_by_file(tts,mp3_txt_file,out_mp3)  
            time.sleep(1) 
         
        # 注意发现字幕是英文比较准确：可考虑先转en 再翻译过来 
        #创建字幕：如果是非润色就直接翻译
        en_srt_file = path +"/" + SOUND_SRT  
        if not os.path.exists(en_srt_file):
            whisper_all(out_mp3, path,True,"srt")
            time.sleep(1)  
        # srt_file = en_srt_file
        srt_file =   path +"/" + "county.srt"  
        if not os.path.exists(srt_file):
            trans_language_By_GTP(en_srt_file,srt_file,whisper)     
            
        # 没有声音视频
        video_no_sound = root_path + "/" + MUTE_VIDEO
        if not os.path.exists(video_no_sound):
            video_no_sound =  random_file(VIDEO_PATH)
        
        # 背景音效 
        bg_sound = None 
        if add_bg_sound:
           bg_sound = random_file(BG_SOUND)
        title = "video"
        # 视频输出路径
        cur_video = video_no_sound
        force_out = path + "/0_force_" + title+".mp4"
        cut_out = path + "/1_cut_" + title+".mp4"
        source_out = path + "/2_sound_" + title+".mp4"
        mark_vdieo = path + "/3_mark_"+title+".mp4"
        srt_mp4 =  path + "/4_srt_" + title+".mp4"
        concat_video = path + "/5_concat_"+title+".mp4"

        # 视频源是否是横屏
        source_L =  is_video_L(video_no_sound) 
        # 是否强制修改视频为横 + 本身就不是横视频 
        if enable_shu_video and not source_L :
            if not os.path.exists(force_out):
                bg_png =  random_file(BG_IMAGE_PATH)
                combine_video_with_bg(cur_video, bg_png,get_video_length(cur_video) ,force_out,1280, 720)
                time.sleep(1)  
            cur_video =  force_out  
            
        #裁剪视频
        if cut_start > 0 or cut_end > 0:
            if not os.path.exists(cut_out):
               crop_video(cur_video,cut_out,cut_start,cut_end)
            cur_video  = cut_out
        
        # 合成音效合成视频
        if not os.path.exists(source_out): 
            # w,h  = get_video_size(cur_video)
            if source_L:
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
        if enable_mark:
            if not os.path.exists(mark_vdieo):
                mark =  random_file(MARK_IMAGE)
                add_mark_to_video(cur_video,mark,mark_vdieo)
                time.sleep(1)
            cur_video = mark_vdieo    
               
        
        # 添加字幕
        if add_srt:
            if not os.path.exists(srt_mp4):
                combine_srt(cur_video,srt_file,srt_mp4)
            cur_video = srt_mp4
            
    
        #合并3个视频  
        if  enable_top_video:
            if not os.path.exists(concat_video) :
                if  enable_shu_video or source_L:
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
     
        
    
                    
reptileMgr = reptile_video()
