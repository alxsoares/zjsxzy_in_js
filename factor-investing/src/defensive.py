# encoding: utf-8

import pandas as pd
import numpy as np
import os

import data

def get_k_day_volatility(code,
                         days=5,
                         start_date="2012-01-01",
                         end_date="2017-01-01"):
    """
    获得k日波动率
    """
    fname = data.get_filename(code)
    df = data.read_data(fname)
    df = df[df.index >= start_date]
    factor_name = "%d-day volatility"%(days)
    df["return"] = df["close"].pct_change()
    df[factor_name] = df["return"].rolling(window=days).std() * np.sqrt(243)
    return df[factor_name]
