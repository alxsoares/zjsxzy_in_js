# encoding: utf-8

import pandas as pd
from numpy import cumsum, log, polyfit, sqrt, std, subtract

import utils

DATA_DIR = "C:\Users\jgtzsx01\Documents\workspace\data\stocks"

'''
    Hurst exponent helps test whether the time series is:
    (1) A Random Walk (H ~ 0.5)
    (2) Trending (H > 0.5)
    (3) Mean reverting (H < 0.5)
'''
def hurst(ts):
    """Returns the Hurst Exponent of the time series vector ts"""
    # Create the range of lag values
    lags = range(2, 100)

    # Calculate the array of the variances of the lagged differences
    tau = [sqrt(std(subtract(ts[lag:], ts[:-lag]))) for lag in lags]

    # Use a linear fit to estimate the Hurst Exponent
    poly = polyfit(log(lags), log(tau), 1)

    # Return the Hurst exponent from the polyfit output
    return poly[0]*2.0

def get_k_day_hurst(code, k, periods=5):
    df = pd.read_excel("%s/%s.xlsx"%(DATA_DIR, code), index_col=0)
    df.index = pd.to_datetime(df.index, format="%Y-%m-%d")
    print("calculating hurst...")
    df["hurst"] = df["close"].rolling(window=k).apply(lambda x: hurst(x)).shift(periods) # 当期k日因子
    df["return"] = df["close"].pct_change(periods=periods) # 下期收益率
    return df[["hurst", "return"]]
