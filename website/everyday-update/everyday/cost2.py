# encoding: utf-8
# 计算个股真实换手率，用以计算其平均持有成本

import pandas as pd
import numpy as np
from WindPy import w
import datetime
import os

import const
import utils

STOCK_DIR = 'D:Data/stocks2'
BY_STOCK_DIR = 'D:Data/avg_cost2/by stock'

'''
def convert_cost_turnover_days(df, stock):
    old_df = pd.read_excel('%s/%s'%(const.BY_STOCK_DIR, stock), index_col=0)
    assert(old_df.shape[0] == df.shape[0])
    k = 0
    dates = df.index
    for i, index in enumerate(dates):
        if df[df.index <= index]["turnover"].sum() < 1:
            continue
        # 双指针维护一段区间使得该区间内的换手率总和正好大于等于1
        prev_index = df.index[k]
        while df[(df.index >= prev_index) & (df.index <= index)]["turnover"].sum() > 1 and k < df.shape[0] - 1:
            k += 1
            prev_index = df.index[k]
        k -=1
        prev_index = df.index[k]
        old_df.loc[index, 'turnover days'] = i - k
    return old_df

def change_turnover_days():
    files = [f for f in os.listdir('D:Data/stocks') if f.endswith("xlsx")]

    for stock in files:
        print("processing %s..."%(stock))
        fname = "%s/%s"%('D:Data/stocks', stock)
        df = pd.read_excel(fname, index_col=0)
        df.to_excel(fname)
        df = convert_cost_turnover_days(df, stock)
        df.to_excel("%s/%s"%(BY_STOCK_DIR, stock))
'''

def convert_cost(df, stock):
    """
    计算历史的成本和100%换手天数
    """
    # 产生一个新的文件
    df.loc[:, "turnover days"] = np.nan # 换手天数
    df.loc[:, "avg cost"] = np.nan # 平均持有成本
    df.loc[:, "profit percentage"] = np.nan # 盈利持仓占比
    k = 0
    dates = df.index

    old_df = pd.read_excel('%s/%s'%(const.BY_STOCK_DIR, stock), index_col=0)
    # old_df = old_df.reset_index().drop_duplicates(subset='index', keep='last').set_index('index')
    # old_df = old_df.sort_index()
    row = ['turnover days', 'avg cost', 'profit percentage']
    df.loc[df.index >= old_df.index[0], row] = old_df[row]

    for i, index in enumerate(dates):
        if not pd.isnull(df.loc[index, 'turnover days']):
            break
        if df[df.index <= index]["turnover"].sum() < 1:
            continue
        # 双指针维护一段区间使得该区间内的换手率总和正好大于等于1
        prev_index = df.index[k]
        while df[(df.index >= prev_index) & (df.index <= index)]["turnover"].sum() > 1 and k < df.shape[0] - 1:
            k += 1
            prev_index = df.index[k]
        k -=1
        prev_index = df.index[k]

        # (prev_index, index)这段区间里的换手率总和正好大于等于1
        temp_df = df[(df.index >= prev_index) & (df.index <= index)]
        cost = (temp_df["vwap"] * temp_df["amt"]).sum() / temp_df["amt"].sum()
        current_price = df.loc[index, 'close']
        profit_volume = temp_df[temp_df['vwap'] < current_price]['volume'].sum()
        profit_percentage = profit_volume / temp_df['volume'].sum()
        df.loc[index, "avg cost"] = cost
        # df.loc[index, "turnover days"] = (index - prev_index).days
        df.loc[index, "turnover days"] = i - k
        df.loc[index, "profit percentage"] = profit_percentage
    return df[["turnover days", "avg cost", "close", "profit percentage"]]

def get_history_turnover():
    files = [f for f in os.listdir(STOCK_DIR) if f.endswith("xlsx")]

    for stock in files:
        print("processing %s..."%(stock))
        # if os.path.exists('%s/%s'%(BY_STOCK_DIR, stock)):
            # continue
        fname = "%s/%s"%(STOCK_DIR, stock)
        df = pd.read_excel(fname, index_col=0)
        # df = df.reset_index().drop_duplicates(subset='index', keep='last').set_index('index')
        # df = df.sort_index()
        # df.to_excel(fname)
        df = convert_cost(df, stock)
        df.to_excel("%s/%s"%(BY_STOCK_DIR, stock))

def get_codes(index_code):
    df = pd.read_excel("%s/%s.xlsx"%(const.INDEX_DIR, index_code))
    return df["code"].tolist()

def get_wind_data(code, start_date, end_date):
    fields = "mkt_freeshares,vwap,amt,close,dealnum,free_turn,volume,mfd_buyamt_a,mfd_sellamt_a,high,low"
    # data = w.wsd(code, fields, beginTime=start_date, endTime=end_date, "PriceAdj=F")
    # data = w.wsd("000402.SZ", "mkt_freeshares,vwap,amt,close", "2017-03-15", "2017-03-16", "PriceAdj=F")
    w.start()
    # print code, start_date, end_date
    data = w.wsd(code, fields, start_date, end_date, "traderType=1;PriceAdj=F")
    # print data
    return utils.wind2df(data)

def get_wind_data_all(index_code, start_date, end_date):
    codes = get_codes(index_code)
    for code in codes:
        fname = 'D:Data/temp/%s.xlsx'%(code)
        # if os.path.exists(fname):
            # continue
        print('downloading %s...'%(code))
        df = get_wind_data(code, start_date, end_date)
        df["turnover"] = df["amt"] / df["mkt_freeshares"] # 计算换手率
        df.to_excel(fname)

def merge_data(index_code):
    codes = get_codes(index_code)
    for code in codes:
        print('merging %s'%(code))
        fname1, fname2 = '%s/%s.xlsx'%(STOCK_DIR, code), 'D:Data/temp/%s.xlsx'%(code)
        df1 = pd.read_excel(fname1, index_col=0)
        df2 = pd.read_excel(fname2, index_col=0)
        # df2 = df2[df2.index < '2015-01-01']
        df = df2.append(df1)
        fname = '%s/%s.xlsx'%(STOCK_DIR, code)
        df.to_excel(fname)

if __name__ == '__main__':
    # get_wind_data_all('881001', '2012-10-01', '2012-12-31')

    # merge_data('881001')
    get_history_turnover()
