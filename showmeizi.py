import os
import time
import re

import requests
from bs4 import BeautifulSoup

FILE_PATH = '/Users/mcode/Desktop/bbbbbb/'
URL = 'https://www.showmeizi.com'
MODEL = '/category/bijini/?currentPage='
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.68'
}


def get_total_page():
    f1_url = URL + MODEL + '1000'
    f1 = get_data(f1_url)
    f1bs4 = BeautifulSoup(f1, 'html.parser')
    page = f1bs4.find('div', {'class': 'page'}).find('a')['href']
    pages = re.compile(r'(?<=currentPage=)\d*').search(page).group()
    print(pages)
    return int(pages)


def get_data(url):
    try:
        r = requests.get(url, headers=headers)
        r.encoding = r.apparent_encoding
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(e)


def parse_data(html):
    smzbs4 = BeautifulSoup(html, 'html.parser')
    piclist = smzbs4.find('div', {'class': 'piclist'}).find_all('a')
    for item in piclist:
        # 图片集地址
        link = item['href']
        # 图片集名字
        name = item['alt']
        url = URL + link
        try:
            tmpbs4 = BeautifulSoup(get_data(url), 'html.parser')
            tmp_list = tmpbs4.find('div', {'class': 'swiper-wrapper'}).find_all('img', {'class': 'swiper-lazy'})
            pics_url = []
            for x in range(0, len(tmp_list)):
                pic_url = URL + tmp_list[x]['data-src']
                pics_url.append(pic_url)
            download_pic(pics_url, name)
        except Exception as e:
            print(e)


def download_pic(pics_url, filename):
    try:
        if not os.path.exists(os.path.join(FILE_PATH, filename)):
            os.mkdir(os.path.join(FILE_PATH, filename))
        os.chdir(FILE_PATH + filename)

        try:
            print('开始下载%s'%filename)
            for pic in pics_url:
                img = requests.get(pic, headers=headers)
                with open(pic[-8:], 'wb') as f:
                    f.write(img.content)
            print('%s已经保存完毕'%filename)
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    start = time.time()
    pages = get_total_page()
    for i in range(0, pages):
        tmp_url = URL + MODEL + '%s' % i
        html = get_data(tmp_url)
        parse_data(html)
    time = time.time()-start
    print(time)