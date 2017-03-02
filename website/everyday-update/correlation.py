# encoding: utf-8
import pandas as pd

import wind_data
import const

def get_data(symbol, start_date, end_date):
    fname = "%s/%s.csv"%(const.DATA_DIR, symbol)
    wind_data.download_data(symbol)
    df = pd.read_csv(fname)
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
    df = df.set_index('date')
    df = df[(df.index >= start_date) & (df.index <= end_date)]
    df['return'] = df['close'].pct_change()
    df.dropna(inplace=True)
    return df

def get_dataframe(symbol1, symbol2, start_date, end_date):
    df1 = get_data(symbol1, start_date, end_date)
    df2 = get_data(symbol2, start_date, end_date)

    if df1.index[0] != df2.index[0]:
        df1 = df1[df1.index >= df2.index[0]]
        df2 = df2[df2.index >= df1.index[0]]
    assert(df1.shape == df2.shape)

    # ks = [5] + range(10, 500, 10)
    ks = range(20, 500, 10)
    df = pd.DataFrame(index=df1.index)
    for look_back in ks:
        df["%d day cor"%(look_back)] = df1['return'].rolling(window=look_back).corr(df2['return'])
    today = df.index[-2]
    data_df = pd.DataFrame({'days': ks, 'cor': df.ix[today].values,
                            'max': df.max(axis=0).values, 'min': df.min(axis=0).values,
                            'median': df.median(axis=0).values,
                            'percent_75': df.quantile(0.75, axis=0).values,
                            'percent_25': df.quantile(0.25, axis=0).values})

    return data_df
