# encoding: utf-8
import pandas as pd
import os
import datetime
from WindPy import w

import const
import utils

def get_data(symbol):
    if not symbol.endswith('.OF'):
        fname = '%s/%s.xlsx'%(const.FOF_DIR, symbol)
        if os.path.exists(fname):
            df = pd.read_excel(fname, index_col=0)
        else:
            today = datetime.datetime.today().strftime('%Y-%m-%d')
            w.start()
            data = w.wsd(symbol, 'close', '2015-01-01', today)
            df = utils.wind2df(data)
            df['return'] = df['close'].pct_change()
            df.to_excel(fname)
        return df[['return']]
    else:
        fname = "%s/history/%s.xlsx"%(const.DATA_DIR, symbol)
        if os.path.exists(fname):
            df = pd.read_excel(fname, index_col=0)
            df['return'] = df['nav_adj'].pct_change()
            return df[['return']]
        else:
            print fname
            return pd.DataFrame()

def get_dataframe(symbol1, symbol2):
    df1 = get_data(symbol1)
    df2 = get_data(symbol2)
    print df2.head()

    if df1.empty or df2.empty:
        return pd.DataFrame()

    if df1.index[0] != df2.index[0]:
        df1 = df1[df1.index >= df2.index[0]]
        df2 = df2[df2.index >= df1.index[0]]
    if df1.index[-1] != df2.index[-1]:
        df1 = df1[df1.index <= df2.index[-1]]
        df2 = df2[df2.index <= df1.index[-1]]
    if df1.shape != df2.shape:
        print('error of shape')
        return pd.DataFrame()

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
