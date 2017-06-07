# encoding: utf-8

import json
import gensim
import datetime
import argparse
import pickle
import pandas as pd

import utils
import const

DATA_DIR = "C:/Users/jgtzsx01/Documents/workspace/data"
# WORD_COUNT_FILE = "%s/wallstreetcn_words/wallstreetcn_word_count.json"%(DATA_DIR)
# TOTAL_WORD_COUNT_FILE = "%s/wallstreetcn_words/wallstreetcn_total_word_count.json"%(DATA_DIR)

def get_total_word_count():
    """
    统计周总词频并scale然后保存到文件
    """
    # print("loading weekly word count file...")
    # with open(WEEKLY_WORD_COUNT_FILE, 'r') as f:
    # with open(const.WORD_COUNT_FILE, 'r') as f:
        # word_cnt = json.load(f)
    with open(const.WORD_CNT_FILE, 'rb') as fp:
        word_cnt = pickle.load(fp)
    print("calculating total word count...")
    total_word_count = {}
    for word in word_cnt:
        for day, value in word_cnt[word].iteritems():
            if not total_word_count.has_key(day):
                total_word_count[day] = 0
            total_word_count[day] += value
    df = pd.DataFrame({'date': total_word_count.keys(), 'count': total_word_count.values()})
    df.index = pd.to_datetime(df['date'], format="%Y-%m-%d")
    df.sort_index(inplace=True)
    df.to_csv("temp.csv", index=False)
    with open(const.TOTAL_WORD_COUNT_FILE, 'wb') as f:
        pickle.dump(total_word_count, f)
    # with open(const.TOTAL_WORD_COUNT_FILE, 'w') as f:
        # json.dump(total_word_count, f)

if __name__ == "__main__":
    get_total_word_count()
