#!/usr/bin/python
# coding:utf-8

import jieba
import jieba.analyse
import os
import datetime
import pandas as pd
import tushare as ts
import gensim
import argparse
import re
import sys
import json
import numpy as np

data_dir = "C:/Users/jgtzsx01/Documents/workspace/data/sina"
csv_dir = "%s/day-news"%(data_dir)
key_words_dir = "%s/week-keywords"%(data_dir)
word_count_file = "%s/word_count.json"%(data_dir)
hot_val = "%s/hot_word_val.json"%(data_dir)
with open("%s/stop_words_zh.txt"%(data_dir), 'r') as f:
    stop_words = set([line.strip() for line in f.readlines()])

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", help="update news or not (y/n)", default='n', type=str)
    parser.add_argument("--week", help="extract key words of the certain number of week", default=0, type=int)
    parser.add_argument("--words", help="update word count (y/n)", default='n', type=str)
    args = parser.parse_args()
    args.update = True if args.update == 'y' else False
    args.words = True if args.words == 'y' else False
    if args.week == 0:
        args.week = datetime.date.today().isocalendar()[1]
    return args

def update_word_count():
    with open(word_count_file, 'r') as f:
        word_cnt = json.load(f)
    files = [f for f in os.listdir(csv_dir)]
    for f in files:
        date = f.split('.')[0]
        print("Processing %s..."%(date))
        df = pd.read_csv("%s/%s"%(csv_dir, f))
        for i in df.index:
            if not isinstance(df["content"][i], str):
                continue
            word_list = [word for word in jieba.cut(df["content"][i]) if not word.encode('utf-8') in stop_words]
            for word in word_list:
                if not word_cnt.has_key(word):
                    word_cnt[word] = {}
                if not word_cnt[word].has_key(date):
                    word_cnt[word][date] = 0
                word_cnt[word][date] += 1

    with open(word_count_file, 'w') as f:
        json.dump(word_cnt, f)

def update_news():
    df = ts.get_latest_news(show_content=True, top=5000)
    df["date"] = df["time"].map(lambda x: "2017-" + x.split(' ')[0])
    dates = df["date"].unique()
    for date in dates:
        date_df = df[df["date"] == date]
        print date_df.shape
        filename = "%s%s.csv"%(csv_dir, date)
        print filename
        if os.path.exists(filename):
            old_df = pd.read_csv(filename)
            if old_df.shape[0] < date_df.shape[0]:
                date_df.to_csv(filename, index=False, encoding='utf-8')
        else:
            date_df.to_csv(filename, index=False, encoding='utf-8')

def get_week_df(week_num):
    files = [f for f in os.listdir(csv_dir)]
    df = pd.DataFrame()
    for f in files:
        date = datetime.datetime.strptime(f.split(".")[0], "%Y-%m-%d")
        (year, week, _) = date.isocalendar()
        if week_num == week:
            print date
            filename = "%s%s.csv"%(csv_dir, date.strftime("%Y-%m-%d"))
            date_df = pd.read_csv(filename)
            if df.empty:
                df = date_df
            else:
                df = df.append(date_df, ignore_index=True)
    return df

def extract_week_keyword(week_num):
    filename = "%s2017-week-%d.csv"%(key_words_dir, week_num)
    if os.path.exists(filename):
        return
    df = get_week_df(week_num)
    df = df[df["classify"] == "国内财经"]
    df.index = range(df.shape[0])

    f = open("./text", 'w')
    count = {}
    topK = 20
    for i in df.index:
        if not isinstance(df.content[i], str):
            continue
        tags = jieba.analyse.textrank(df["content"][i], withWeight=True, topK=topK, allowPOS=('ns', 'n', 'vn', 'v'))
        doc = " ".join([word.encode("utf-8") for word in jieba.cut(df["content"][i]) if not word.encode('utf-8') in stop_words])
        f.write(doc + "\n")

        for word, weight in tags:
            if not count.has_key(word):
                count[word] = 0
            count[word] += weight
    f.close()
    sort_count = sorted(count.iteritems(), key=lambda x: x[1], reverse=True)

    os.system("python word2vec.py ./text model vector")
    model = gensim.models.Word2Vec.load("model")

    dic = {"rank": [], "word": [], "related words": []}
    for i, (word, _) in enumerate(sort_count):
        if not word in model.vocab:
            print word
            continue
        dic["rank"].append(i + 1)
        dic["word"].append(word)
        result = model.most_similar(word, topn=20)
        related = u"，".join([x[0] for x in result])
        dic["related words"].append(related)
    out_df = pd.DataFrame(dic)
    out_df.columns = ["rank", "word", "related words"]
    out_df.to_csv(filename, index=False, encoding='utf-8')

if __name__ == "__main__":
    args = get_args()
    if args.words:
        update_word_count()
