# -*- coding:utf-8 -*-
# 对mzitu爬虫的一次模仿
#


import re  # 需要使用正则表达式对数据进行筛选
import os  # 需要进行文件的删除与创建
import time
import threading
from multiprocessing import Pool, cpu_count

import requests
from bs4 import BeautifulSoup


headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Referer': 'http://www.mzitu.com'
}


DIR_PATH = r"D:\mzitu"


def get_urls():
    page_urls = ["http://www.mzitu.com/page/{cnt}".format(cnt=cnt) for cnt in range(1, 197)]
    print('Please wait for second...')
    img_urls = []
    for page_url in page_urls:
        try:
            bs = BeautifulSoup(requests.get(page_url, headers=headers, timeout=30).text,
                               'lxml').find('ul', id='pins')
            result = re.findall(r"(?<=href=)\S+", str(bs))
            img_url = [url.replace('"', "") for url in result]
            img_urls.extend(img_url)
        except Exception as e:
            print(e)
    return set(img_urls)


lock = threading.Lock()


def mzitu_crawler(url):
    try:
        r =requests.get(url, headers=headers, timeout=30).text
        folder_name = BeautifulSoup(r, 'lxml').find(
            'div', class_='main-image').find('img')['alt'].replace("?"," ")
        with lock:
            if make_dir(folder_name):
                max_count = BeautifulSoup(r, 'lxml').find(
                    'div', class_='pagenavi').find_all('span')[-2].get_text()
                page_urls = [url + '/' + str(i) for i in range(1, int(max_count) + 1)]
                img_urls = []
                for _, page_url in enumerate(page_urls):
                    time.sleep(0.25)
                    result = requests.get(page_url, headers=headers, timeout=30).text
                    img_url = BeautifulSoup(result, 'lxml').find(
                        'div', class_='main-image').find('p').find('a').find('img')['src']
                    img_urls.append(img_url)
                for cnt, url in enumerate(img_urls):
                    save_pic(cnt, url)
    except Exception as e:
        print(e)


def save_pic(pic_cnt, pic_url):
    try:
        time.sleep(0.10)
        img = requests.get(pic_url, headers=headers, timeout=30)
        img_name = "pic_cnt_{}.jpg".format(pic_cnt + 1)
        with open(img_name, 'ab') as f:
            f.write(img.content)
            print(img_name)
    except Exception as e:
        print(e)


def make_dir(folder_name):
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
    if os.path.exists(save_dir):
        if os.path.isdir(save_dir):
            for d in os.listdir(save_dir):
                path = os.path.join(save_dir, d)
                if os.path.isdir(path):
                    delete_empty_dir(path)
        if not os.listdir(save_dir):
            os.rmdir(save_dir)
            print("remove the empty dir:{}".format(save_dir))
    else:
        print('Please start your performance!')


if __name__ == '__main__':
    urls = get_urls()
    pool = Pool(processes=cpu_count())
    try:
        delete_empty_dir(DIR_PATH)
        pool.map(mzitu_crawler, urls)
    except Exception:
        time.sleep(30)
        delete_empty_dir(DIR_PATH)
        pool.map(mzitu_crawler, urls)