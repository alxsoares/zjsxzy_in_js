# encoding: utf-8

import pandas as pd
import numpy as np
import os
from WindPy import w

import data
import const

def rank_percentile(array):
    """
    返回s的最后一个元素在s中的分位值
    """
    s = pd.Series(array)
    s = s.rank(pct=True)
    return s.iloc[-1]

def get_pe_ratio(code,
                 start_date="2012-01-01",
                 end_date="2017-01-01"):
    """
    获得PE
    """
    w.start()
    raw_data = w.wsd(code, 'pe_ttm', start_date, end_date)
    df = data.wind2df(raw_data)
    return df["pe_ttm"]

def get_pe_ratio_percentile(code,
                            days=243,
                            start_date="2012-01-01",
                            end_date="2017-01-01"):
    """
    获得PE历史百分比
    """
    w.start()
    raw_data = w.wsd(code, 'pe_ttm', start_date, end_date)
    df = data.wind2df(raw_data)
    df["pe_percent"] = df["pe_ttm"].rolling(window=days).apply(rank_percentile)
    return df["pe_percent"]
