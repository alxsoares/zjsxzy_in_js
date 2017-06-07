# encoding: utf-8
import pandas as pd
import numpy as np
import os

import wind_data
import const

def get_data(symbol, start_date, end_date):
    fname = "%s/%s.csv"%(const.DATA_DIR, symbol)
    if not os.path.exists(fname):
        return pd.DataFrame()
    dataframe = pd.read_csv(fname)
    dataframe['date'] = pd.to_datetime(dataframe['date'], format="%Y-%m-%d")
    dataframe = dataframe.set_index('date')
    dataframe = dataframe[(dataframe.index >= start_date) & (dataframe.index <= end_date)]
    # 得到收益率
    dataframe['return'] = dataframe['close'].pct_change()
    dataframe = dataframe[['return']].dropna()
    return dataframe

def get_dataframe(symbol, start_date, end_date):
    dataframe = get_data(symbol, start_date, end_date)
    if dataframe.empty:
        return pd.DataFrame()
    # ks = [5] + range(10, 500, 10)
    ks = range(20, 500, 10)
    df = pd.DataFrame(index=dataframe.index)
    for look_back in ks:
        df['%d days vol'%(look_back)] = dataframe['return'].rolling(window=look_back).std() * np.sqrt(243)
    # df.to_csv("%s_vol.csv"%(asset_select.value))
    today = df.index[-2]
    data_df = pd.DataFrame({'days': ks, 'vol': df.ix[today].values,
                            'max': df.max(axis=0).values, 'min': df.min(axis=0).values,
                            'median': df.median(axis=0).values,
                            'percent_75': df.quantile(0.75, axis=0).values,
                            'percent_25': df.quantile(0.25, axis=0).values})
    return data_df
