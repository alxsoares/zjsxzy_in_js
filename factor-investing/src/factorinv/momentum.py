# encoding: utf-8

import pandas as pd
import numpy as np
import os

import data

def get_k_day_return(code,
                     days=5,
                     start_date="2012-01-01",
                     end_date="2017-01-01"):
    """
    获得k日收益率，计算公式：(当日收盘价-k日前收盘价)/当日收盘价
    """
    fname = data.get_filename(code)
    df = data.read_data(fname)
    df = df[df.index >= start_date]
    factor_name = "%d-day return"%(days)
    df[factor_name] = df['close'].pct_change(periods=days)
    return df[factor_name]

def get_k_day_average_return(code,
                             days=5,
                             start_date="2012-01-01",
                             end_date="2017-01-01"):
    """
    获得k日平均收益率
    """
    fname = data.get_filename(code)
    df = data.read_data(fname)
    df = df[df.index >= start_date]
    factor_name = "%d-day average return"%(days)
    df["return"] = df['close'].pct_change()
    df[factor_name] = df["return"].rolling(window=days).mean()
    return df[factor_name]
