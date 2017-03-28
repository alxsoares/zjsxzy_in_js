# encoding: utf-8
import pandas as pd

import utils

DATA_DIR = "C:\Users\jgtzsx01\Documents\workspace\data\stocks"

def get_k_day_return(code, k, periods=5):
    df = pd.read_excel("%s/%s.xlsx"%(DATA_DIR, code), index_col=0)
    df.index = pd.to_datetime(df.index, format="%Y-%m-%d")
    df["momentum"] = df["close"].pct_change(periods=k).shift(periods) # 当期k日因子
    df["return"] = df["close"].pct_change(periods=periods) # 下期收益率
    return df[["momentum", "return"]]
