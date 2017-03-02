# encoding: utf-8

from WindPy import w
import numpy as np

import utils

w.start()

def get_data(asset_code, start_date, end_date):
    data = w.wsd(asset_code, 'close', start_date, end_date)
    df = utils.wind2df(data)
    df.index.name = "date"
    return df

def get_dataframe(asset_code, look_back, start_date, end_date):
    df = get_data(asset_code, start_date, end_date)
    df['return'] = df['close'].pct_change()
    # 标准化价格
    df['price'] = (1 + df['return']).cumprod()[1:] - 1
    # 过去look_back天的平均收益率
    df['avg_return'] = df['return'].rolling(window=look_back).mean() * 30
    # 过去look_back天的夏普率
    df['sharpe'] = df['return'].rolling(window=look_back).mean() * np.sqrt(243) / df['return'].rolling(window=look_back).std() / 30
    return df[['price', 'avg_return', 'sharpe']]
