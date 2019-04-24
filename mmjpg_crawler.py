# -*- coding:utf-8 -*-
# 对mmjpg爬虫的一次模仿
#


import os  # 用于文件夹的创建与删除
import time  # 用于对访问进行时间控制
import threading  # 用于多进程访问，加快速度
from multiprocessing import Pool, cpu_count  # 用于进程池的使用

import requests  # 用于发送网络请求，返回响应数据
from bs4 import BeautifulSoup  # 用于从html或xml提取数据


headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                  ' AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/69.0.3497.100 Safari/537.36',
    'Referer': 'www.mmjpg.com'
}


DIR_PATH = r"D:\mmjpg"  # 用于存放文件的地址


def save_pic(pic_cnt, pic_url):
    """
    将图片下载到本地文件夹
    """
    try:
        img = requests.get(pic_url, headers=headers, timeout=10)
        img_name = "pic_cnt_{}.jpg".format(pic_cnt + 1)
        with open(img_name, 'ab') as f:
            f.write(img.content)
            print(img_name)
    except Exception as e:
        print(e)


def make_dir(folder_name):
    """
    根据传来的文件名，在指定路径下创建文件
    """
    path = os.path.join(DIR_PATH, folder_name)
    if not os.path.exists(path):
        os.makedirs(path)
        print(path)
        os.chdir(path)
        return True
    else:
        print('Folder has existed!')
        return False


def delete_empty_dir(save_dir):
    """
    在进行爬虫前，将路径中的空文件删除
    """
    if os.path.exists(save_dir):
        if os.path.isdir(save_dir):
            for d in os.listdir(save_dir):
                path = os.path.join(save_dir, d)
                if os.path.isdir(path):
                    delete_empty_dir(path)
        if not os.listdir(save_dir):
            os.rmdir(save_dir)
            print("remove the empty dir :{}".format(save_dir))
    else:
        print('Please start your performance!')


lock = threading.Lock()


def urls_crawler(url):
    """
    爬虫入口，主要进行爬取操作
    """
    try:
        r = requests.get(url, headers=headers, timeout=10).text
        # 从lxml中获取套图名字用于文件夹命名
        folder_name = BeautifulSoup(r, 'lxml').find(
            'h2').text.encode('ISO-8859-1').decode('utf-8')
        with lock:
            if make_dir(folder_name):
                # 得出套图张数
                max_count = BeautifulSoup(r, 'lxml').find(
                    'div', class_='page').find_all('a')[-2].get_text()
                # 得到页面url
                page_urls = [url + '/' + str(i) for i in range(1, int(max_count) + 1)]
                img_urls = []
                # 得到图片地址
                for index, page_url in enumerate(page_urls):
                    result = requests.get(page_url, headers=headers, timeout=10).text
                    if index + 1 < len(page_urls):
                        img_url = BeautifulSoup(result, 'lxml').find(
                            'div', class_='content').find('a').img['src']
                        img_urls.append(img_url)
                    else:
                        img_url = BeautifulSoup(result, 'lxml').find(
                            'div', class_='content').find('img')['src']
                        img_urls.append(img_url)

                for cnt, url in enumerate(img_urls):
                    save_pic(cnt, url)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    urls = ["http://mmjpg.com/mm/{cnt}".format(cnt=cnt) for cnt in range(1, 2000)]
    pool = Pool(processes=cpu_count())
    try:
        delete_empty_dir(DIR_PATH)
        pool.map(urls_crawler, urls)
    except Exception as e:
        time.sleep(30)
        delete_empty_dir(DIR_PATH)
        pool.map(urls_crawler, urls)