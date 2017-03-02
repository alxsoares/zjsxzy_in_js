# encoding: utf-8
# 统计华尔街见闻新闻文本的词频

from os.path import join, dirname
import jieba
import datetime
import os
import json
import utils

import total_word_count

DATA_DIR = "C:/Users/jgtzsx01/Documents/workspace/data/"
WALLSTCN_DIR = "%s/wallstreetcn"%(DATA_DIR)
CSRC_DIR = "%s/CSRC"%(DATA_DIR)
CBRC_DIR = "%s/CBRC"%(DATA_DIR)
CIRC_DIR = "%s/CIRC"%(DATA_DIR)
WORD_CNT_FILE = "%s/wallstreetcn_words/wallstreetcn_word_count.json"%(DATA_DIR)
WORD_CNT_CHECKED_FILE = "%s/wallstreetcn_words/wallstreetcn_word_count_checked.txt"%(DATA_DIR)
years = ['2016', '2017']
with open(join(dirname(__file__), "stop_words_zh.txt"), 'r') as f:
    stop_words = set([line.strip() for line in f.readlines()])

def update_wallst_word_count():
    with open(WORD_CNT_FILE, 'r') as fp:
        word_count = json.load(fp)
    with open(WORD_CNT_CHECKED_FILE, 'r') as fp:
        checked_list = [line.strip() for line in fp.readlines()]
    for y in years:
        files = ["%s/%s/%s"%(WALLSTCN_DIR, y, f) for f in os.listdir("%s/%s/"%(WALLSTCN_DIR, y))]
        print y, len(files)
        if len(files) > 0:
            for f in files:
                if f in checked_list:
                    continue
                with open(WORD_CNT_CHECKED_FILE, 'a') as fp:
                    fp.write(f + '\n')
                with open(f, 'r') as fp:
                    text = fp.readlines()
                time = text[0].split('_')[0]
                time = time.strip()
                dt = datetime.datetime.strptime(time, "%Y年%m月%d日 %H:%M:%S")
                date = dt.strftime("%Y-%m-%d")

                content = " ".join(text[1:])
                doc = [word for word in jieba.cut(content) if not word in stop_words]
                for word in doc:
                    """
                    if not utils.isChinese(word):
                        continue
                    """
                    if utils.isNumber(word):
                        continue
                    if not word_count.has_key(word):
                        word_count[word] = {}
                    if not word_count[word].has_key(date):
                        word_count[word][date] = 0
                    word_count[word][date] += 1

    with open(WORD_CNT_FILE, 'w') as fp:
        json.dump(word_count, fp)

def update_circ_word_count():
    with open(WORD_CNT_FILE, 'r') as fp:
        word_count = json.load(fp)
    with open(WORD_CNT_CHECKED_FILE, 'r') as fp:
        checked_list = [line.strip() for line in fp.readlines()]
    for y in years:
        files = [f for f in os.listdir("%s/%s/"%(CIRC_DIR, y))]
        print y, len(files)
        if len(files) > 0:
            for f in files:
                if f in checked_list:
                    continue
                with open(WORD_CNT_CHECKED_FILE, 'a') as fp:
                    fp.write(f + '\n')
                date = f.split('_')[0]
                f = "%s/%s/%s"%(CIRC_DIR, y, f)
                with open(f, 'r') as fp:
                    text = fp.readlines()

                content = " ".join(text)
                doc = [word for word in jieba.cut(content) if not word in stop_words]
                for word in doc:
                    if utils.isNumber(word):
                        continue
                    if not word_count.has_key(word):
                        word_count[word] = {}
                    if not word_count[word].has_key(date):
                        word_count[word][date] = 0
                    word_count[word][date] += 1
    with open(WORD_CNT_FILE, 'w') as fp:
        json.dump(word_count, fp)

def update_cbrc_word_count():
    with open(WORD_CNT_FILE, 'r') as fp:
        word_count = json.load(fp)
    with open(WORD_CNT_CHECKED_FILE, 'r') as fp:
        checked_list = [line.strip() for line in fp.readlines()]
    for y in years:
        files = [f for f in os.listdir("%s/%s/"%(CBRC_DIR, y))]
        print y, len(files)
        if len(files) > 0:
            for f in files:
                if f in checked_list:
                    continue
                with open(WORD_CNT_CHECKED_FILE, 'a') as fp:
                    fp.write(f + '\n')
                date = f.split('_')[0]
                f = "%s/%s/%s"%(CBRC_DIR, y, f)
                with open(f, 'r') as fp:
                    text = fp.readlines()

                content = " ".join(text)
                doc = [word for word in jieba.cut(content) if not word in stop_words]
                for word in doc:
                    if utils.isNumber(word):
                        continue
                    if not word_count.has_key(word):
                        word_count[word] = {}
                    if not word_count[word].has_key(date):
                        word_count[word][date] = 0
                    word_count[word][date] += 1
    with open(WORD_CNT_FILE, 'w') as fp:
        json.dump(word_count, fp)

def update_csrc_word_count():
    with open(WORD_CNT_FILE, 'r') as fp:
        word_count = json.load(fp)
    with open(WORD_CNT_CHECKED_FILE, 'r') as fp:
        checked_list = [line.strip() for line in fp.readlines()]
    for y in years:
        files = [f for f in os.listdir("%s/%s/"%(CSRC_DIR, y))]
        print y, len(files)
        if len(files) > 0:
            for f in files:
                if f in checked_list:
                    continue
                with open(WORD_CNT_CHECKED_FILE, 'a') as fp:
                    fp.write(f + '\n')
                date = f.split('_')[0]
                f = "%s/%s/%s"%(CSRC_DIR, y, f)
                with open(f, 'r') as fp:
                    text = fp.readlines()

                content = " ".join(text)
                doc = [word for word in jieba.cut(content) if not word in stop_words]
                for word in doc:
                    if utils.isNumber(word):
                        continue
                    if not word_count.has_key(word):
                        word_count[word] = {}
                    if not word_count[word].has_key(date):
                        word_count[word][date] = 0
                    word_count[word][date] += 1
    with open(WORD_CNT_FILE, 'w') as fp:
        json.dump(word_count, fp)

def update_all_word_count():
    update_circ_word_count()
    update_cbrc_word_count()
    update_csrc_word_count()
    update_wallst_word_count()

if __name__ == "__main__":
    update_all_word_count()
    total_word_count.get_total_word_count()
