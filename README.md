![1693644496977](https://github.com/StartHua/AI-/assets/22284244/0c10b136-1b7a-4493-bf91-0b5b64c59cb1)
![image](https://github.com/StartHua/AI-/assets/22284244/11118dea-0da3-4bdc-8f3c-05ac9977a8cb)
一.开发此项目目的，为了短视频创作自动化，也是一次ai实用化,功能基本已经完成,有能力的自行修改！python！

二.项目支持youtobe,titko,抖音，bilibili视频下载（youtobe，tiko需要翻墙注意不要全局，因为sd Fooocus 会报错）.

三.自动化项目逻辑原理：
    开启二次创作：
      (1).下载视频.
      (2).预处理: 1.分解出视频 mute.mp4静音视频 + 语音sound.mp3
                  2.使用openai-whisper对mp3文件进行翻译获取原始字幕文件srt和内容文件txt.
      (3).用户选择视频国家，进行二次创作。
          1.对分离出来的mute.mp4进行二次创作,支持基础功能：
              a.添加背景音乐(背景音乐放到assets/bg_sound目录下随机的)
              b.添加水印右下方(图标mark放到assets/mark目录洗随机)
              c.添加字幕
              b.添加头尾(随机添加)这里分横竖屏幕，视频头放到assets/head/head_L(横屏) head_V(竖屏)
                尾部：assets/bottom/bottom_L(横) bottom_V(竖)
                注意：默认视频1280*768  ，768*1280
              c.强制横屏:本身是横屏情况下不处理，如果是竖屏就是添加一个背景底图（asset/bg_image随机）  
              d.删除头尾（秒）：一些视频有开始会有一些频道介绍就可以使用这功能，注意尾部是倒数开始切的。
              e.保留视频宽高:一般情况下宽不变计算是从中心开始把两边按比例去掉，高保留不同是从底部开始计算为了去掉一些视频字幕区域。
                  一般情况不需要改宽保持1.
          2.开启GPT润色。(使用GPT+提示词prompt对分离出来的内容文件txt进行处理重新生成相识的文案生成embellish.txt) 
          3.经行国家处理。
            a.使用google_tran和GPT对之前生成的润色文案或者是原本的sound.txt经行翻译成该国语音。
            b.使用egg_tts对生成文案生成选择国家的语音文件mp3,再使用openai-whisper对音频生产字幕文件 .
            c.使用 ffmpeg 经行视频处理（基于上面选项经行一步步处理会比较慢，其实可以优化多步合并）

      开启SD创作（最好使用sd创作关闭二创）sd_task.py:
          (1).预处理和上面一样.
          (2).使用sd（Stable Diffusion）调用api形式生产图片。这里我使用不是Stable Diffusion而是https://github.com/lllyasviel/Fooocus可以算sd子项目原理一样
              好处是简单。自己搭建。端口：7860
          (3).写好一个功能强大的提示词整个sd创作精华去访问GPT让它生产一个sd_video.json创作脚本。这个去看config/config.py里面SD_PROMPT。
          (4).对刚刚sd_video.json进行处理，api调用sd生产图片序列帧存放到img目录下。egg_tts生产每一句话的语言存放到sound目录下。代码处理文本生成每一句的字幕文件放到srt目录下。
              判断上面对应数据合并成一个小视频放到video目录下.最后把所有的小视频合并成完整视频。
              为什么一句一个小视频？因为这样字幕语言比较准确！

四.安装。
   1.环境python3.9 ,安装cuda环境https://pytorch.org/get-started/locally/,推荐使用conda
   2.pip install -r requirements.txt (国内网络不行加上-i https://pypi.douban.com/simple)  遇到包安装问题自行解决百度谷歌，GPT去问。
   3.安装ffmpeg环境添加到环境变量里。
   4.这里需要用到openai-whisper 模型放到model下 model/large-v2.pt  model/medium.pt
   5.python app.py（网页）  或者python main.py（exe版本没有sd功能建议app.py）

五.项目是花了差不多10天左右时间所做，代码功能还需要优化。但是功能基本齐全了，有能力就改，或者参考来做都可以，原理就这样。

六.启动后发现生成的没有生成视频，可以再启动，会基于上次生成素材基础上工作。因为每次启动都会保存配置。还有就是不要一次输入太多链接生产太多不然容易出这问题，还需要修改！    

七.电脑牛的可以开启多线程操作，默认max_workers=1 修改app.py .       

八.后面有时间会对代码经行重构，放出更多的参数,这是一次尝试！希望能帮助到大家！

九.个人：AI正在改变这个世界，有时间多多关照这方面，能在工作，生活上带来很大改变！学习ai技术不要陷入到训练大模型里面去，等开源模型，不过最好能训练一次微型模型就够，除非专业搞NLP！
做了这么久ai技术研究（非NLP算法开发）开发得出一个结论：GPT+本地数据库+prompt基本可以解决80%问题！


