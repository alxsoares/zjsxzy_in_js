import pandas as pd
import os

import wind_data
import const

def get_dataframe(symbol, start_date, end_date):
    fname = "%s/%s.csv"%(const.DATA_DIR, symbol)
    if not os.path.exists(fname):
        return pd.DataFrame()
    # wind_data.download_data(symbol)
    dataframe = pd.read_csv(fname)
    dataframe.dropna(inplace=True)
    dataframe['date'] = pd.to_datetime(dataframe['date'], format="%Y-%m-%d")
    dataframe = dataframe.set_index('date')
    dataframe = dataframe[(dataframe.index >= start_date) & (dataframe.index <= end_date)]
    dataframe = dataframe.resample('BM').last()
    return dataframe
