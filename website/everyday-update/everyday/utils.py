import pyfolio as pf
from WindPy import w
import numpy as np
import pandas as pd
import os

import const

w.start()

def wind2df(raw_data):
    dic = {}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[str(field.lower())] = data
    return pd.DataFrame(dic, index=raw_data.Times)

def get_money_fund_daily_return(start_date, end_date):
    code = "H11025.CSI"
    fname = '%s/%s.csv'%(const.DATA_DIR, code)
    if os.path.exists(fname):
        df = pd.read_csv(fname, index_col=0)
    else:
        data = w.wsd(code, 'close', start_date, end_date)
        df = wind2df(data)
        df['return'] = df['close'].pct_change()
        df.to_csv(fname)
    return df['return'].dropna()

def get_sharpe_ratio(daily_return):
    sharpe_ratio = pf.empyrical.sharpe_ratio(daily_return)
    # return sharpe_ratio
    start_date = daily_return.index[0]
    end_date = daily_return.index[-1]
    days = int((end_date - start_date).days)
    acc_return = (1 + daily_return).cumprod()[-1]

    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    money_daily_return = get_money_fund_daily_return(start_date, end_date)
    money_acc_return = (1 + money_daily_return).cumprod()[-1]

    volatility = daily_return.std() * np.sqrt(243)

    sharpe_ratio = (acc_return**(365./days) - money_acc_return**(365./days)) / volatility
    return sharpe_ratio

def roll(df, w):
    """
    This fucntion comes from:
    http://stackoverflow.com/questions/37486502/why-does-pandas-rolling-use-single-dimension-ndarray/37491779#37491779
    """
    df.fillna(df.mean(), inplace=True)
    roll_array = np.dstack([df.values[i:i+w, :] for i in range(len(df.index) - w + 1)]).T
    panel = pd.Panel(roll_array,
                     items=df.index[w-1:],
                     major_axis=df.columns,
                     minor_axis=pd.Index(range(w), name='roll'))
    return panel.to_frame().unstack().T.groupby(level=0)

def get_index_component(index_code):
    index_file = "%s/%s.xlsx"%(const.INDEX_DIR, index_code)
    df = pd.read_excel(index_file)
    return df['code'].tolist()
