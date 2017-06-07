# encoding: utf-8
# 下载华尔街见闻新闻文本，需要给定一个起始的node id，可以从最新的文章的url中找

import urllib2
from bs4 import BeautifulSoup
import httplib
import datetime
import os
import requests
import sys
import time as T

import crawl_gov

DATA_DIR = "C:/Users/jgtzsx01/Documents/workspace/data"
WALLSTCN_DIR = "%s/wallstreetcn"%(DATA_DIR)
CSRC_DIR = "%s/CSRC"%(DATA_DIR)
CBRC_DIR = "%s/CBRC"%(DATA_DIR)
CIRC_DIR = "%s/CIRC"%(DATA_DIR)

def get_latest_node():
    url = 'http://wallstreetcn.com'
    response = requests.get(url)
    text = response.text.encode('utf-8')
    soup = BeautifulSoup(text, "html.parser")
    news = soup.find_all(class_='home-news-item__main')
    for ele in news:
        href = ele.find('a').get('href')
        if href.startswith('/articles/'):
            return int(href.split('/')[-1])

def crawl_wallst(start_node=3010475):
    PAGE_NOT_FOUND_FILE = "%s/page_not_found.txt"%(DATA_DIR)
    with open(PAGE_NOT_FOUND_FILE, 'r') as fp:
        page_not_found_list = [int(line.strip()) for line in fp.readlines()]
    years = [y for y in os.listdir(WALLSTCN_DIR)]
    downloaded = []
    for y in years:
        files = [int(f[:-4]) for f in os.listdir("%s/%s/"%(WALLSTCN_DIR, y))]
        downloaded += files
    print downloaded[-10:]
    print page_not_found_list[-10:]

    downloaded = set(downloaded)
    page_not_found_list = set(page_not_found_list)
    print "total articles: %d"%(len(downloaded))

    BASE_URL = "http://wallstreetcn.com/articles"
    # conn = httplib.HTTPConnection("wallstreetcn.com")
    for node_id in range(start_node, 3000000, -1):
        # if node_id % 10000 == 0:
            # print "iteration %d"%(node_id)
        if node_id in downloaded or node_id in page_not_found_list:
        # if node_id in downloaded:
            continue
        url = "%s/%d"%(BASE_URL, node_id)
        # print "checking url %s"%(node_id)
        try:
            # conn.request('GET', url)
            # response = conn.getresponse()
            # text = response.read()
            response = requests.get(url)
            text = response.text
            text = text.encode("utf-8")
            soup = BeautifulSoup(text, "html.parser")
            title = soup.title.get_text()
            if title == "Page Not Found":
                with open(PAGE_NOT_FOUND_FILE, 'a') as f:
                    f.write(str(node_id) + '\n')
                continue
            if title == u"华尔街见闻 - 华尔街见闻":
                with open(PAGE_NOT_FOUND_FILE, 'a') as f:
                    f.write(str(node_id) + '\n')
                continue
            print title
            content = soup.find(class_="page-article-content")
            if content == None:
                content = soup.find(class_="node-article-content")
            content = content.get_text()
            # time = soup.find(class_="title-meta-time").contents[-1]
            # if time == None:
            time = soup.find(class_='meta-item__text').get_text()
            year = time[:4]
            author = soup.find(class_="author-meta-name")
            if author == None:
                author = soup.find(class_="title-meta-source")
            if author == None:
                author = soup.find(class_="article__author__meta__item__name")
            if author == None:
                author = "no author"
            else:
                author = author.get_text().lstrip().rstrip()

            filename = "%s/%s/%d.txt"%(WALLSTCN_DIR, str(year), node_id)
            if os.path.exists(filename):
                continue
            print "saving to file: ", filename
            information = "%s_%s_%s"%(
                time.encode('utf-8'),
                author.encode('utf-8'),
                title.encode('utf-8')
            )
            with open(filename, 'w') as f:
                f.write(information + "\n")
                f.write(content.encode('utf-8'))
        except Exception as e:
            print("%d error occured"%(node_id))
            print(str(e))
            T.sleep(10)

'''
def crawl_csrc(page_id=49):
    BASE_URL = "http://www.csrc.gov.cn/pub/newsite/zjhxwfb/xwdd/"
    CSRC_url = []
    for i in range(page_id+1):
        if i == 0:
            CSRC_url.append(BASE_URL)
        else:
            CSRC_url.append(BASE_URL + "index_%s.html"%str(i))

    conn = httplib.HTTPConnection("www.csrc.gov.cn")
    for url in CSRC_url:
        conn.request('GET', url)
        response = conn.getresponse()
        text = response.read()
        soup = BeautifulSoup(text, 'html.parser')

        article_list = soup.find(class_='fl_list')
        for li in article_list.findAll("li"):
            print li
            item = li.find('a')
            date = li.find('span').string
            if date == None:
                continue
            year = date.split('-')[0]
            article_url = BASE_URL + item.get("href")[2:]
            print article_url
            if not article_url.endswith(".html"):
                continue

            conn = httplib.HTTPConnection("www.csrc.gov.cn")
            conn.request('GET', article_url)
            response = conn.getresponse()
            text = response.read()
            soup = BeautifulSoup(text, 'html.parser')

            title = soup.title.string
            content = soup.find(class_='content').get_text()

            fname = "%s/%s/%s_%s.txt"%(CSRC_DIR, year, date, title)
            if os.path.exists(fname):
                break
            try:
                with open(fname, 'w') as f:
                    f.write(content.encode('utf-8'))
            except:
                print url

def crawl_cbrc(page_id=47):
    BASE_URL = "http://www.cbrc.gov.cn/chinese/home/docViewPage/110010"
    cbrc_urls = [BASE_URL+"&current=%d"%(i) for i in range(1, page_id+1)]
    conn = httplib.HTTPConnection("www.cbrc.gov.cn")
    for url in cbrc_urls:
        conn.request('GET', url)
        response = conn.getresponse()
        text = response.read()
        soup = BeautifulSoup(text, 'html.parser')

        article_list = soup.find(class_='xia3')
        for li in article_list.findAll("tr"):
            item = li.find('a')
            article_url = "http://www.cbrc.gov.cn" + item.get('href')
            if not article_url.endswith(".html"):
                continue
            date = li.findAll('td')[-1].get_text().strip()
            year = date.split('-')[0]

            conn = httplib.HTTPConnection("www.cbrc.gov.cn")
            conn.request('GET', article_url)
            response = conn.getresponse()
            text = response.read()
            print article_url
            soup = BeautifulSoup(text, 'html.parser')

            title = soup.title.string
            content = soup.find(class_="Section0")
            if content == None:
                content = soup.find(class_="Section1")
            if content == None:
                content = soup.find(class_="WordSection1")
            if content == None:
                content = soup.find(class_="n_cent")
            content = content.get_text()
            fname = "%s/%s/%s_%s.txt"%(CBRC_DIR, year, date, title)
            if os.path.exists(fname):
                continue
            try:
                with open(fname, 'w') as f:
                    f.write(content.encode('utf-8'))
            except:
                print article_url

def crawl_circ(page_id=47):
    BASE_URL = "http://www.circ.gov.cn/web/site0/tab5207/module14337"
    circ_urls = [BASE_URL+"/page%d.htm"%(i) for i in range(1, page_id+1)]
    conn = httplib.HTTPConnection("www.circ.gov.cn")
    for url in circ_urls:
        conn.request('GET', url)
        response = conn.getresponse()
        text = response.read()
        soup = BeautifulSoup(text, 'html.parser')

        article_list = soup.find(class_="muban1")
        for li in article_list.findAll("tr"):
            item = li.find('a')
            if item.get("href") != None and item.get('href').startswith("/web"):
                date = li.findAll("td")[-1].get_text()
                if date[0] == '(':
                    date = '20' + date.lstrip('(').rstrip(')')
                    year = date.split('-')[0]
                    article_url = "http://www.circ.gov.cn" + item.get('href')

                    conn = httplib.HTTPConnection("www.circ.gov.cn")
                    conn.request('GET', article_url)
                    response = conn.getresponse()
                    text = response.read()
                    soup = BeautifulSoup(text, 'html.parser')

                    title = soup.title.string
                    content = soup.find(id="zoom").get_text()

                    fname = "%s/%s/%s_%s.txt"%(CIRC_DIR, year, date, title)
                    fname = fname.replace('\n', '').replace('\r', '').replace('\t', '')
                    try:
                        print fname
                        if os.path.exists(fname):
                            continue
                        with open(fname, 'w') as f:
                            f.write(content.encode('utf-8'))
'''

def main():
    node = get_latest_node()
    crawl_wallst(node)
    crawl_gov.update()

if __name__ == "__main__":
    main()
