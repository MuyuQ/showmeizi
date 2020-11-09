# -- coding: utf-8 --
# @Time : DATEDATE{TIME}
# @Author : Mcode
"""
多线程爬showmeizi网图片
"""

import os
import threading
import time
import re

import requests
from bs4 import BeautifulSoup
from requests import HTTPError

FILE_PATH = '/Users/mcode/Desktop/bbbbbb/'
URL = 'https://www.showmeizi.com'
MODEL = '/category/bijini'
SUFFIX = '/?currentPage='
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,\
    */*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
    AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.68'
}


def get_total_page():
    """
    计算总页数,确定爬虫边界
    :return: 总页数
    """
    page_count_url = URL + MODEL + SUFFIX + '1000'
    tmp = get_data(page_count_url)
    f1bs4 = BeautifulSoup(tmp, 'html.parser')
    page = f1bs4.find('div', {'class': 'page'}).find('a')['href']
    pagenum = re.compile(r'(?<=currentPage=)\d*').search(page).group()
    return int(pagenum)


def get_data(url):
    """
    获取对应url的网页信息
    :param url: 目标url
    :return: 返回网页信息,传递给进行数据处理的函数
    """
    try:
        req = requests.get(url, headers=headers)
        req.encoding = req.apparent_encoding
        req.raise_for_status()
        return req.text
    except requests.RequestException:
        print('获取地址出错')


def parse_data(html):
    """
    处理传入的网页信息,将整理后的下载列表传递给负责下载的函数download_pic(url,filename)
    :param html: 网页信息
    :return: 需要下载的图片地址列表
    """
    smzbs4 = BeautifulSoup(html, 'html.parser')
    piclist = smzbs4.find('div', {'class': 'piclist'}).find_all('a', {'target': '_blank'})
    for item in piclist:
        # 图片集地址
        link = item['href']
        # 图片集名字
        name = item['alt']
        url = URL + link
        try:
            tmpbs4 = BeautifulSoup(get_data(url), 'html.parser')
            tmp_list = tmpbs4.find('div', {'class': 'swiper-wrapper'}). \
                find_all('img', {'class': 'swiper-lazy'})
            pics_url = []
            for index, tmp in enumerate(tmp_list):
                pic_url = URL + tmp_list[index]['data-src']
                pics_url.append(pic_url)
        except HTTPError:
            print('保存pics出错')
        download_pic(pics_url, filename=name)


def download_pic(pics_url, filename):
    """
    将传入的图片地址列表下载
    :param pics_url:  图片下载地址列表
    :param filename: 图片集名称
    :return: none
    """
    try:
        if not os.path.exists(os.path.join(FILE_PATH, filename)):
            os.mkdir(os.path.join(FILE_PATH, filename))
        os.chdir(FILE_PATH + filename)
    except os.error:
        print('检测目录出错')
    print('开始下载%s' % filename)
    for pic in pics_url:
        try:
            img = requests.get(pic, headers=headers)
        except ConnectionError:
            print('下载出错')
        with open(pic[-8:], 'wb') as file:
            file.write(img.content)
    print('%s下载完毕' % filename)


if __name__ == '__main__':
    start = time.time()
    pages = get_total_page()
    html = []
    threads = []
    for i in range(0, pages):
        tmp_url = URL + MODEL + SUFFIX + '%s' % i
        if i == 0:
            tmp_url = URL + MODEL
        html.append(get_data(tmp_url))
        threads.append(threading.Thread(target=parse_data, args=(html[i],)))
    for t in threads:
        t.start()

    time = time.time() - start
    print(time)
