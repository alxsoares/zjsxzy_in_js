import urllib2
from bs4 import BeautifulSoup
import httplib
import datetime
import os
import requests
import sys

def wallstreet_crawl(start_node=286749):
    base_url = "http://wallstreetcn.com/node"
    wallstreetcn_data_dir = "C:\Users\jgtzsx01\Documents\workspace\data\wallstreetcn"
    conn = httplib.HTTPConnection("wallstreetcn.com")
    for node_id in range(start_node, 0, -1):
        url = "%s/%d"%(base_url, node_id)
        conn.request('GET', url)
        response = conn.getresponse()
        text = response.read()
        soup = BeautifulSoup(text, "html.parser")

        title = soup.title.get_text()
        if title == "Page Not Found":
            continue
        print node_id
        try:
            content = soup.find(class_="page-article-content").get_text()
            time = soup.find(class_="title-meta-time").contents[-1]
            year = time[:4]
            author = soup.find(class_="author-meta-name").get_text()

            filename = "%s/%s/%d.txt"%(wallstreetcn_data_dir, str(year), node_id)
            print filename
            if os.path.exists(filename):
                continue
            information = "%s_%s_%s"%(
                time.encode('utf-8'),
                author.encode('utf-8'),
                title.encode('utf-8')
            )
            with open(filename, 'w') as f:
                f.write(information + "\n")
                f.write(content.encode('utf-8'))
        except:
            with open("error_list.txt", 'a') as f:
                f.write("%d\n"%(node_id))

if __name__ == "__main__":
    if sys.argv[1] == 'WS':
        wallstreet_crawl()
