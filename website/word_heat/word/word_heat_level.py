# encoding: utf-8
# 提取某一个关键词在历史新闻文本中的热度并保存到csv文件中

import json
import pickle
import gensim
import datetime
import argparse
import os
import pandas as pd

import utils
import const

print("loading word count file...")
# with open(WORD_COUNT_FILE, 'r') as f:
    # word_count = json.load(f)
with open(const.WORD_COUNT_FILE, 'rb') as fp:
    word_count = pickle.load(fp)
# with open(TOTAL_WORD_COUNT_FILE, 'r') as f:
    # total_word_count = json.load(f)
with open(const.TOTAL_WORD_COUNT_FILE, 'rb') as f:
    total_word_count = pickle.load(f)
print("loading word vector model...")
model = gensim.models.Word2Vec.load(const.WALLSTCN_MODEL)

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
                  look_back=5):

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
    df = pd.DataFrame({'date': total_word_count.keys(), 'count': total_word_count.values()})
    df.index = pd.to_datetime(df['date'], format="%Y-%m-%d")
    df.sort_index(inplace=True)
    df = df[df.index >= '2016-01-01']
    # print df.tail()

    heat_df = pd.DataFrame({"date": heat_count.keys(),
                            "absolute": heat_count.values(),
                            'relative': heat_count_relative.values(),
                            'weighted': heat_count_weighted.values()})
    heat_df.index = heat_df["date"].map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))
    heat_df.sort_index(inplace=True)
    heat_df['total'] = df['count']
    # print heat_df.tail()
    # 滚动k日
    heat_df.loc[:, 'total'] = heat_df['total'].rolling(window=look_back).sum()
    heat_df.loc[:, 'absolute'] = heat_df['absolute'].rolling(window=look_back).sum()
    heat_df.loc[:, 'relative'] = heat_df['relative'].rolling(window=look_back).sum() * 100. / heat_df['total']
    heat_df.loc[:, 'weighted'] = heat_df['weighted'].rolling(window=look_back).sum() * 100. / heat_df['total']

    similar_df.to_csv("%s/%s_%.1f_words.csv"%(const.ASSET_CLASS_DIR, key_word, threshold), index=False, encoding="utf-8")
    heat_df.to_csv("%s/%s_%.1f.csv"%(const.ASSET_CLASS_DIR, key_word, threshold), index=False)

def calculate_words():
    with open('%s/words.txt'%(const.WORD_HEAT_DIR), 'r') as f:
        words = [w.strip().decode('utf-8') for w in f.readlines()]
    for word in words:
        print word
        get_word_heat(word)

def rank_percentile(array):
    """
    返回s的最后一个元素在s中的分位值
    """
    s = pd.Series(array)
    s = s.rank(pct=True)
    return s.iloc[-1]

def get_words_percentile():
    with open('%s/words.txt'%(const.WORD_HEAT_DIR), 'r') as f:
        words = [w.strip().decode('utf-8') for w in f.readlines()]
    dic = {}
    for word in words:
        fname = '%s/%s_0.5.csv'%(const.ASSET_CLASS_DIR, word)
        df = pd.read_csv(fname)
        dic[word] = rank_percentile(df['weighted'])
    df = pd.DataFrame({'word': dic.keys(), 'percentile': dic.values()})
    df.to_excel('%s/percentile.xlsx'%(const.WORD_HEAT_DIR), index=False)

def get_correlation(s1, s2):
    start_date = '2016-03-01'
    end_date = min(s1.index[-1], s2.index[-1])
    s1 = s1[(s1.index >= start_date) & (s1.index <= end_date)]
    s2 = s2[(s2.index >= start_date) & (s2.index <= end_date)]
    df = pd.DataFrame({'s1': s1, 's2': s2}, index=s1.index)
    rolled_df = utils.roll(df, 60)
    corr = rolled_df.apply(lambda df: df['s1'].corr(df['s2']))
    return corr

def word_asset_correlation():
    word_files = [f for f in os.listdir(const.WORD_DIR) if f.find('words') == -1]
    asset_files = [f for f in os.listdir(const.ASSET_DIR) if f.endswith('.csv')]
    words = [w[:-4] for w in word_files]
    words = [unicode(w, 'gbk').split('_')[0] for w in words]
    assets = [a[:-4] for a in asset_files]

    absolute_df = pd.DataFrame({'word': []}, index=words, columns=assets)
    relative_df = pd.DataFrame({'word': []}, index=words, columns=assets)
    absolute_df['word'] = words
    relative_df['word'] = words
    for w, wf in zip(words, word_files):
        for a in assets:
            print w, a
            wdf = pd.read_csv('%s/%s'%(const.WORD_DIR, wf))
            adf = pd.read_csv('%s/%s.csv'%(const.ASSET_DIR, a))
            wdf.index = pd.to_datetime(wdf['date'], format='%Y-%m-%d')
            adf.index = pd.to_datetime(adf['date'], format='%Y-%m-%d')
            corr = get_correlation(wdf['relative'], adf['close'])
            absolute_corr, relative_corr = corr[-1], utils.rank_percentile(corr)
            absolute_df.loc[w, a] = absolute_corr
            relative_df.loc[w, a] = relative_corr
    absolute_df.to_excel('%s/absolute_corr.xlsx'%(const.WORD_HEAT_DIR), float_format='%.2f', index=False)
    relative_df.to_excel('%s/relative_corr.xlsx'%(const.WORD_HEAT_DIR), float_format='%.2f', index=False)

def main():
    # pass
    calculate_words()
    # word_asset_correlation()
    get_words_percentile()

if __name__ == "__main__":
    main()
