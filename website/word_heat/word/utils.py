# encoding: utf-8

import re
import pandas as pd
import numpy as np

def isChinese(word):
    for w in word:
        if re.match('[ \u4e00 -\u9fa5]+',w) == None:
            continue
        else:
            return False
    return True

def isEnglish(word):
    try:
        word.decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        print word
        return True

def isNumber(word):
    try:
        float(word)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(word)
        return True
    except (TypeError, ValueError):
        pass
    return False

def isWORD(word):
    if isChinese(word):
        return True
    if isEnglish(word):
        return True
    return False

def rank_percentile(array):
    """
    返回s的最后一个元素在s中的分位值
    """
    s = pd.Series(array)
    s = s.rank(pct=True)
    return s.iloc[-1]

def roll(df, w):
    """
    This fucntion comes from:
    http://stackoverflow.com/questions/37486502/why-does-pandas-rolling-use-single-dimension-ndarray/37491779#37491779
    """
    df.fillna(df.mean(), inplace=True)
    roll_array = np.dstack([df.values[i:i+w, :] for i in range(len(df.index) - w + 1)]).T
    panel = pd.Panel(roll_array,
                     items=df.index[w-1:],
                     major_axis=df.columns,
                     minor_axis=pd.Index(range(w), name='roll'))
    return panel.to_frame().unstack().T.groupby(level=0)
