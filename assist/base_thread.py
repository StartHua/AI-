import threading
import concurrent.futures
import asyncio

class BaseThread:
    def __init__(self, max_workers=5):
        self.downloaded = {}  # 用于跟踪下载状态
        self.callback = None  # 用于存储回调函数
        self.all_callback = None  # 全部下载完成回调
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.running_threads = []

    def set_callback(self, callback):
        self.callback = callback

    def set_all_callback(self, callback):
        self.all_callback = callback

    def download(self, url, args):
        # 这里是你的下载逻辑
        print(f"完成下载 {url}")
        self.downloaded[url] = True
        if self.callback:
            self.callback(url, args)
        self.running_threads.remove(threading.current_thread())

    def download_in_thread(self, url, args):
        if not self.executor._shutdown:  # 检查线程池是否已关闭
            thread = self.executor.submit(self.download, url, args)
            self.running_threads.append(thread)

    def stop_all_threads(self):
        for thread in self.running_threads:
            thread.cancel()
        self.running_threads = []

    def download_all(self, url_list, args):
        for url in url_list:
            self.download_in_thread(url, args)

        self.executor.shutdown(wait=True)
        print("所有下载任务已完成！")
        if self.all_callback:
            self.all_callback(args)
        self.reset()

    def reset(self):
        self.stop_all_threads()
        # 重置线程池，以便可以再次提交新的下载任务
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.executor._max_workers)
        self.downloaded = {}