# encoding: utf-8

import urllib2
from bs4 import BeautifulSoup
import httplib
import datetime
import os
import requests

import const

def crawl_content(url):
    conn = httplib.HTTPConnection("www.gov.cn")
    conn.request('GET', url)
    response = conn.getresponse()
    text = response.read()
    soup = BeautifulSoup(text, "html.parser")

    title = soup.title.text
    title = title.split('_')[0]
    title = title.replace('"', '').replace('|', '').replace('/', '').replace(u'、', '').replace(u'？', '')
    date_source = soup.find(class_='pages-date')
    if date_source == None:
        return
    date_source = date_source.text.split('\n')[0]
    date, source = date_source.split(u'来源：')
    if date.startswith(u'中央政府门户网站'):
        date = date.split('www.gov.cn')[1]
    date, source = date.lstrip().rstrip(), source.lstrip().rstrip()
    date = date.replace(':', '-')
    source = source.replace(u'网站', '')
    content = soup.find(class_='pages_content')
    if content == None:
        return
    content = content.text
    dir_name = '%s/%s'%(const.GOV_DIR, source)
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    fname = '%s/%s_%s.txt'%(dir_name, date, title)
    if os.path.exists(fname):
        return True
    try:
        print date, title
    except Exception as e:
        pass
    with open(fname, 'w') as f:
        f.write(content.encode('utf-8'))
    return False

def crawl_sector(sector_name, update_mode=False):
    base_url = 'http://sousuo.gov.cn/column/%s'%(sector_name)
    url_list = ['%s/%d.htm'%(base_url, i) for i in range(2000)]
    for list_url in url_list:
        conn = httplib.HTTPConnection("sousuo.gov.cn")
        conn.request('GET', list_url)
        response = conn.getresponse()
        text = response.read()
        soup = BeautifulSoup(text, "html.parser")
        article_list = soup.find(class_='listTxt')
        if article_list == None:
            return
        for li in article_list.findAll("li"):
            item = li.find('a')
            url, title = item.get('href'), item.text
            try:
                downloaded = crawl_content(url)
            except Exception as e:
                print(e)
                with open('./error.txt', 'a') as f:
                    f.write(url + '\n')
                print(url)
            if update_mode and downloaded:
                return

def update():
    crawl_sector('30611', update_mode=True) # 滚动
    crawl_sector('30612', update_mode=True) # 政务联播
    crawl_sector('30613', update_mode=True) # 部门
    crawl_sector('30614', update_mode=True) # 中央
    crawl_sector('30618', update_mode=True) # 部门
    crawl_sector('30624', update_mode=True) # 图片
    crawl_sector('30625', update_mode=True) # 时政
    crawl_sector('30626', update_mode=True) # 社会
    crawl_sector('30627', update_mode=True) # 地方
    crawl_sector('30593', update_mode=True) # 专家
    crawl_sector('30474', update_mode=True) # 部门
    crawl_sector('40048', update_mode=True) # 媒体
    crawl_sector('31421', update_mode=True) # 要闻

def crawl():
    crawl_sector('30611') # 滚动
    crawl_sector('30612') # 政务联播
    crawl_sector('30613') # 部门
    crawl_sector('30614') # 中央
    crawl_sector('30618') # 部门
    crawl_sector('30624') # 图片
    crawl_sector('30625') # 时政
    crawl_sector('30626') # 社会
    crawl_sector('30627') # 地方
    crawl_sector('30593') # 专家
    crawl_sector('30474') # 部门
    crawl_sector('40048') # 媒体
    crawl_sector('31421') # 要闻

if __name__ == '__main__':
    # crawl()
    update()
    # crawl_content('http://www.gov.cn/xinwen/2017-04/14/content_5185566.htm')
