# encoding: utf-8

import json
import gensim
import pandas as pd

DATA_DIR = "C:/Users/jgtzsx01/Documents/workspace/data"
WORD_COUNT_FILE = "%s/wallstreetcn_words/wallstreetcn_word_count.json"%(DATA_DIR)
WALLSTCN_MODEL = "C:/Users/jgtzsx01/Documents/workspace/model/wallstreet_model"
ASSET_CLASS_DIR = "%s/asset-class"%(DATA_DIR)

key_word = u"欧洲"

def main(key_word):
    with open(WORD_COUNT_FILE, 'r') as f:
        word_count = json.load(f)
    heat_val = word_count[key_word].copy()
    """
    model = gensim.models.Word2Vec.load(WALLSTCN_MODEL)
    for word, dis in model.most_similar(key_word, topn=10):
        if word in word_count:
            for day, value in word_cnt[word].iteritems():
                if not heat_val.has_key(day):
                    heat_val[day] = 0
                heat_val[day] += value
    """
    heat_df = pd.DataFrame({'date': heat_val.keys(), 'value': heat_val.values()})
    heat_df.to_csv("%s/wallstreetcn_words/%s.csv"%(DATA_DIR, key_word), index=False)

if __name__ == "__main__":
    main(key_word)
