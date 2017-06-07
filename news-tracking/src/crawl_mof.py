# encoding: utf-8
# 下载财政部新闻文本

import urllib2
from bs4 import BeautifulSoup
import httplib
import datetime
import os
import requests
import sys
import time as T

import const

BASE_URL = 'http://www.mof.gov.cn/zhengwuxinxi'

def crawl_list_page(base_url, list_url, update_mode=False):
    conn = httplib.HTTPConnection("www.mof.gov.cn")
    conn.request('GET', list_url)
    response = conn.getresponse()
    text = response.read()
    soup = BeautifulSoup(text, "html.parser")
    article_list = soup.find(class_='ZIT')
    if article_list == None:
        return
    print list_url

    for li in article_list.findAll("tr"):
        item = li.find('td')
        elements = item.text.split('\n')
        elements = [x.lstrip().rstrip() for x in elements if x.lstrip().rstrip() != '']
        if len(elements) < 2:
            continue
        title = elements[0]
        date = elements[1].lstrip(u'（').rstrip(u'）')
        fname = '%s/%s/%s_%s.txt'%(const.MOF_DIR, date[:4], date, title)
        if os.path.exists(fname):
            if update_mode:
                return
            else:
                continue

        item = li.find('a')
        url = item.get('href')
        if not url.startswith('http'):
            url = os.path.join(base_url, url)
        print url

        if url.endswith('htm') or url.endswith('html'):
            conn.request('GET', url)
            response = conn.getresponse()
            text = response.read()
            soup = BeautifulSoup(text, "html.parser")
            content = soup.find(class_='TRS_Editor')
            if content == None:
                continue
            if content.style == None:
                content = content.text
            else:
                content = content.text.replace(content.style.text, '')

            print fname
            with open(fname, 'w') as f:
                f.write(content.encode('utf-8'))

def crawl(sector_name):
    base_url = '%s/%s/'%(BASE_URL, sector_name)
    url_list = [base_url] + ['%sindex_%d.htm'%(base_url, i) for i in range(1, 100)]
    for url in url_list:
        crawl_list_page(base_url, url)

if __name__ == '__main__':
    # crawl('zhengcefabu') # 政策发布
    # crawl('caizhengxinwen') # 财政新闻
    # crawl('zhengcejiedu') # 政策解读
    crawl('caijingshidian') # 财经视点
