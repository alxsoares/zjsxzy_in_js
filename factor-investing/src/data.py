# encoding: utf-8

from WindPy import w
import pandas as pd
import numpy as np
import os

import const


def wind2df(raw_data):
    """
    把wind数据转换成dataframe
    """
    dic = {}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[str(field.lower())] = data
    return pd.DataFrame(dic, index=raw_data.Times)

def get_filename(code):
    """
    得到对应代码的本地文件地址
    """
    fname = "%s/%s.xlsx"%(const.DATA_DIR, code)
    return fname

def get_factor_filename(code, frequency='d'):
    """
    得到对应代码的因子本地文件地址
    """
    if frequency == 'd':
        fname = "%s/%s_factors.xlsx"%(const.DATA_DIR, code)
    if frequency == 'm':
        fname = "%s/%s_month_factors.xlsx"%(const.DATA_DIR, code)
    return fname

def read_data(fname):
    """
    读取excel表，输出dataframe
    """
    if not os.path.exists(fname):
        code = fname.split('/')[-1].split('.')
        code = '.'.join(code[:-1])
        print("Downloading %s..."%(code))
        download_data(code)
    df = pd.read_excel(fname, index_col=0)
    return df

def download_data(code):
    """
    从wind上下载对应代码的数据
    """
    w.start()
    data = w.wsd(code, "close", const.START_DATE, const.END_DATE)
    df = wind2df(data)
    fname = get_filename(code)
    df.to_excel(fname)
    fname = get_factor_filename(code)
    df.to_excel(fname)

def get_close(code):
    """
    获取日度收盘价格
    """
    fname = get_filename(code)
    df = read_data(fname)
    return df['close']

def get_frequency_df(df, frequency='m'):
    """
    根据frequency resample数据
    """
    if frequency == 'm':
        return df.resample('M').last()
    if frequency == 'y':
        return df.resample('A').last()

def save_factor(code, factor_name, series):
    """
    把factor计算结果保存到文件
    """
    fname = get_factor_filename(code)
    factor_df = read_data(fname)
    assert(factor_df.shape[0] == series.shape[0])
    factor_df[factor_name] = series
    factor_df.to_excel(fname)

if __name__ == "__main__":
    fname = get_factor_filename("CI005021.WI")
    df = read_data(fname)
    print df
