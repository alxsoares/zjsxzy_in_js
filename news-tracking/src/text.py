# encoding: utf-8

from os.path import join, dirname
import jieba
import datetime
import os
import json

import utils

DATA_DIR = "C:/Users/jgtzsx01/Documents/workspace/data/"
TEXT_FILE = '%s/wallstreetcn_text'%(DATA_DIR)
WALLSTCN_DIR = "%s/wallstreetcn"%(DATA_DIR)
years = ['2017']
with open(join(dirname(__file__), "stop_words_zh.txt"), 'r') as f:
    stop_words = set([line.strip() for line in f.readlines()])

def get_wallst_text():
    document = ''
    for y in years:
        files = ["%s/%s/%s"%(WALLSTCN_DIR, y, f) for f in os.listdir("%s/%s/"%(WALLSTCN_DIR, y))]
        print y, len(files)
        if len(files) > 0:
            for f in files:
                with open(f, 'r') as fp:
                    text = fp.readlines()
                time = text[0].split('_')[0]
                time = time.strip()
                if time.find('-') != -1:
                    dt = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M")
                else:
                    dt = datetime.datetime.strptime(time, '%Y年%m月%d日 %H:%M:%S')
                date = dt.strftime("%Y-%m-%d")

                content = " ".join(text[1:])
                doc = [word for word in jieba.cut(content) if (not word in stop_words) and (not utils.isNumber(word))]
                document += '\n' + ' '.join(doc)

    with open(TEXT_FILE, 'w') as fp:
        fp.write(document.encode('utf-8'))

if __name__ == "__main__":
    get_wallst_text()
