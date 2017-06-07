# encoding: utf-8

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
    fname = "%s/%s.xlsx"%(const.STOCK_DIR, code)
    return fname

def get_factor_filename(code):
    """
    得到对应代码的因子本地文件地址
    """
    fname = '%s/%s.xlsx'%(const.FACTOR_DIR, code)
    return fname

def read_data(fname):
    """
    读取excel表，输出dataframe
    """
    if not os.path.exists(fname):
        code = fname.split('/')[-1].split('.')
        code = '.'.join(code[:-1])
        print("Downloading %s..."%(code))
        # download_data(code)
    df = pd.read_excel(fname, index_col=0)
    return df

def save_factor(code, factor_name, series):
    """
    把factor计算结果保存到文件
    """
    fname = get_factor_filename(code)
    factor_df = read_data(fname)
    assert(factor_df.shape[0] == series.shape[0])
    if factor_name in factor_df.columns:
        print('factor already exists')
    else:
        factor_df[factor_name] = series
        factor_df.to_excel(fname)

if __name__ == "__main__":
    codes = [code[:9] for code in os.listdir(const.STOCK_DIR)]
    for code in codes:
        print('processing %s...'%(code))
        fname = get_filename(code)
        df = read_data(fname)
        df['caps'] = df['mkt_freeshares']
        fname = get_factor_filename(code)
        df[['close', 'caps']].to_excel(fname)
