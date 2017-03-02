# encoding: utf-8
# 提取某一个关键词在历史新闻文本中的热度并保存到csv文件中

import json
import gensim
import datetime
import argparse
import pandas as pd

import utils

DATA_DIR = "C:/Users/jgtzsx01/Documents/workspace/data"
WORD_COUNT_FILE = "%s/wallstreetcn_words/wallstreetcn_word_count.json"%(DATA_DIR)
TOTAL_WORD_COUNT_FILE = "%s/wallstreetcn_words/wallstreetcn_total_word_count.json"%(DATA_DIR)
WALLSTCN_MODEL = "C:/Users/jgtzsx01/Documents/workspace/model/wallstreet_model"
ASSET_CLASS_DIR = "%s/asset-class"%(DATA_DIR)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--word", help="key word", default="楼市", type=str)
    args = parser.parse_args()
    args.word = args.word.decode('utf-8')
    return args

def get_word_heat(key_word,
                  threshold=0.5,
                  similar_words=1000,
                  start_date="2016-01-01",
                  end_date=datetime.datetime.today().strftime("%Y-%m-%d"),
                  look_back=7):
    print("loading word count file...")
    with open(WORD_COUNT_FILE, 'r') as f:
        word_count = json.load(f)
    with open(TOTAL_WORD_COUNT_FILE, 'r') as f:
        total_word_count = json.load(f)
    print("loading word vector model...")
    model = gensim.models.Word2Vec.load(WALLSTCN_MODEL)

    heat_count = word_count[key_word].copy()
    heat_count_relative = word_count[key_word].copy()
    heat_count_weighted = word_count[key_word].copy()
    similar_df = pd.DataFrame({"word": [key_word], "distance": [1.0]})
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.today()
    for word, dis in model.most_similar(key_word, topn=similar_words):
        if dis < threshold:
            break
        if not utils.isNumber(word) and word in word_count:
            similar_df.ix[similar_df.shape[0]] = [dis, word]
            for day, value in word_count[word].iteritems():
                if not heat_count.has_key(day):
                    heat_count[day], heat_count_relative[day], heat_count_weighted[day] = 0, 0, 0
                heat_count[day] += value
                heat_count_relative[day] += value
                heat_count_weighted[day] += value * dis

    # 填充当日没有出现词的数据
    current_date = start_date
    while current_date < end_date:
        key = current_date.strftime("%Y-%m-%d")
        if not heat_count.has_key(key):
            heat_count[key], heat_count_relative[key], heat_count_weighted[key] = 0, 0, 0
        if not total_word_count.has_key(key):
            total_word_count[key] = 0
        current_date = current_date + datetime.timedelta(1)

    heat_df = pd.DataFrame({"date": heat_count.keys(),
                            "absolute": heat_count.values(),
                            'relative': heat_count_relative.values(),
                            'weighted': heat_count_weighted.values(),
                            'total': total_word_count.values()})
    heat_df.index = heat_df["date"].map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))
    heat_df.sort_index(inplace=True)
    # 滚动k日
    heat_df.loc[:, 'total'] = heat_df['total'].rolling(window=look_back).sum()
    heat_df.loc[:, 'absolute'] = heat_df['absolute'].rolling(window=look_back).sum()
    heat_df.loc[:, 'relative'] = heat_df['relative'].rolling(window=look_back).sum() * 100. / heat_df['total']
    heat_df.loc[:, 'weighted'] = heat_df['weighted'].rolling(window=look_back).sum() * 100. / heat_df['total']

    similar_df.to_csv("%s/%s_%.1f_words.csv"%(ASSET_CLASS_DIR, key_word, threshold), index=False, encoding="utf-8")
    heat_df.to_csv("%s/%s_%.1f.csv"%(ASSET_CLASS_DIR, key_word, threshold), index=False)

if __name__ == "__main__":
    args = get_args()
    get_word_heat(args.word)
