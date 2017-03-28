# encoding: utf-8
import pandas as pd

import wind_data
import const

def get_dataframe(symbol, start_date, end_date):
    fname = "%s/%s.csv"%(const.DATA_DIR, symbol)
    dataframe = pd.read_csv(fname)
    dataframe.dropna(inplace=True)
    dataframe['date'] = pd.to_datetime(dataframe['date'], format="%Y-%m-%d")
    dataframe['return'] = dataframe['close'].pct_change()
    dataframe = dataframe.set_index('date')
    dataframe.index.name = "date"
    dataframe = dataframe[(dataframe.index >= start_date) & (dataframe.index <= end_date)]

    dataframe['mom5'] = dataframe['close'].pct_change(periods=5) # 过去5日收益率
    dataframe['mom20'] = dataframe['close'].pct_change(periods=20) # 过去一个月收益率
    dataframe['mom40'] = dataframe['close'].pct_change(periods=40) # 过去两个月收益率
    dataframe['mom60'] = dataframe['close'].pct_change(periods=60) # 过去三个月收益率
    # dataframe["mom30"] = dataframe["return"].rolling(window=30).mean() # 过去30个交易日平均收益
    # dataframe["mom60"] = dataframe["return"].rolling(window=60).mean() # 过去60个交易日平均收益
    # dataframe["mom180"] = dataframe["return"].rolling(window=180).mean() # 过去180个交易日平均收益
    dataframe = dataframe.resample('BM').last()
    return dataframe
