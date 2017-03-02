# encoding: utf-8

from WindPy import w
import pandas as pd

import utils

w.start()

def get_data(asset_code, start_date, end_date):
    data = w.wsd(asset_code, 'close', start_date, end_date)
    df = utils.wind2df(data)
    df.index.name = 'date'
    return df

def get_dataframe(stock, index, start_date, end_date):
    stock_df = get_data(stock, start_date, end_date)
    index_df = get_data(index, start_date, end_date)

    stock_df['return'] = stock_df['close'].pct_change()
    index_df['return'] = index_df['close'].pct_change()
    stock_df.dropna(inplace=True)
    index_df.dropna(inplace=True)
    if stock_df.index[0] != index_df.index[0]:
        stock_df = stock_df[stock_df.index >= index_df.index[0]]
        index_df = index_df[index_df.index >= stock_df.index[0]]
    assert(stock_df.shape == index_df.shape)

    ks = range(20, 500, 10)
    df = pd.DataFrame(index=stock_df.index)
    for k in ks:
        df["%d day beta"%(k)] = index_df['return'].rolling(window=k).cov(stock_df['return'])
        df["%d day beta"%(k)] = df["%d day beta"%(k)] / index_df['return'].rolling(window=k).var()
    today = df.index[-2]
    data_df = pd.DataFrame({'days': ks, 'beta': df.ix[today].values,
                            'max': df.max(axis=0).values, 'min': df.min(axis=0).values,
                            'median': df.median(axis=0).values,
                            'percent_75': df.quantile(0.75, axis=0).values,
                            'percent_25': df.quantile(0.25, axis=0).values})

    return data_df
