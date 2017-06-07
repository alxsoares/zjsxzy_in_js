# encoding: utf-8
# 统计华尔街见闻新闻文本的词频

from os.path import join, dirname
import jieba
import datetime
import os
import json
import utils
import pickle

import total_word_count
import const

DATA_DIR = "C:/Users/jgtzsx01/Documents/workspace/data/"
WALLSTCN_DIR = "%s/wallstreetcn"%(DATA_DIR)
# WORD_CNT_FILE = '%s/wallstreetcn_words/word_count.pkl'%(DATA_DIR)
# WORD_CNT_CHECKED_FILE = '%s/wallstreetcn_words/word_count_checked.txt'%(DATA_DIR)
# WORD_CNT_FILE = "%s/wallstreetcn_words/wallstreetcn_word_count.json"%(DATA_DIR)
# WORD_CNT_CHECKED_FILE = "%s/wallstreetcn_words/wallstreetcn_word_count_checked.txt"%(DATA_DIR)
years = ['2016', '2017']
with open(join(dirname(__file__), "stop_words_zh.txt"), 'r') as f:
    stop_words = set([line.strip() for line in f.readlines()])

def update_wallst_word_count():
    # with open(WORD_CNT_FILE, 'r') as fp:
        # word_count = json.load(fp)
    # with open(WORD_CNT_CHECKED_FILE, 'r') as fp:
        # checked_list = [line.strip() for line in fp.readlines()]
    with open(const.WORD_CNT_FILE, 'rb') as fp:
        word_count = pickle.load(fp)
    with open(const.WORD_CNT_CHECKED_FILE, 'r') as fp:
        checked_list = set([line.strip().decode('utf-8') for line in fp.readlines()])
    f_check = open(const.WORD_CNT_CHECKED_FILE, 'a')
    for y in years:
        files = ["%s/%s/%s"%(WALLSTCN_DIR, y, f) for f in os.listdir("%s/%s/"%(WALLSTCN_DIR, y))]
        print y, len(files)
        if len(files) > 0:
            for f in files:
                if f in checked_list:
                    continue
                # with open(WORD_CNT_CHECKED_FILE, 'a') as fp:
                    # fp.write(f + '\n')
                f_check.write(f.encode('utf-8') + '\n')
                with open(f, 'r') as fp:
                    text = fp.readlines()
                time = text[0].decode('utf-8').split('_')[0]
                time = time.strip()
                if time.find('-') == -1:
                    time = time.replace(u'年', '-').replace(u'月', '-').replace(u'日', '')
                '''
                if time.count(':') == 2:
                    dt = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
                else:
                    dt = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
                date = dt.strftime("%Y-%m-%d")
                '''
                date = time.split(' ')[0]

                content = " ".join(text[1:])
                doc = [word for word in jieba.cut(content) if not word in stop_words]
                for word in doc:
                    if utils.isNumber(word):
                        continue
                    if not word_count.has_key(word):
                        word_count[word] = {}
                    if not word_count[word].has_key(date):
                        word_count[word][date] = 0
                    word_count[word][date] += 1

    # with open(WORD_CNT_FILE, 'w') as fp:
        # json.dump(word_count, fp)
    with open(const.WORD_CNT_FILE, 'wb') as fp:
        pickle.dump(word_count, fp)

def update_files(prefix, files):
    with open(const.WORD_CNT_FILE, 'rb') as fp:
        word_count = pickle.load(fp)
    with open(const.WORD_CNT_CHECKED_FILE, 'r') as fp:
        checked_list = set([line.strip().decode('utf-8') for line in fp.readlines()])
    f_check = open(const.WORD_CNT_CHECKED_FILE, 'a')
    for f in files:
        date = f.split('_')[0]
        if not date.startswith('2016') and not date.startswith('2017'):
            continue
        date = date.split(' ')[0]
        f = '%s/%s'%(prefix, f)
        if f in checked_list or not f.endswith('.txt'):
            continue
        f_check.write(f.encode('utf-8') + '\n')
        with open(f, 'r') as fp:
            text = fp.readlines()

        content = ' '.join(text)
        doc = [word for word in jieba.cut(content) if not word in stop_words]
        for word in doc:
            if utils.isNumber(word):
                continue
            if word_count.has_key(word):
                continue
            if not word_count.has_key(word):
                word_count[word] = {}
            if not word_count[word].has_key(date):
                word_count[word][date] = 0
            word_count[word][date] += 1
    with open(const.WORD_CNT_FILE, 'wb') as fp:
        pickle.dump(word_count, fp)

def update_gov_word_count():
    for dep in const.DEPARTMENT:
        prefix = '%s/%s'%(const.GOV_DIR, dep)
        if prefix.endswith('txt'):
            continue
        files = [f for f in os.listdir(prefix)]
        print dep, len(files)
        if len(files) > 0:
            update_files(prefix, files)

def update_all_word_count():
    update_wallst_word_count()
    update_gov_word_count()

def main():
    update_all_word_count()
    total_word_count.get_total_word_count()

if __name__ == "__main__":
    main()
