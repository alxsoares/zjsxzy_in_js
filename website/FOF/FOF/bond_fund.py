# encoding: utf-8

import pandas as pd
import numpy as np
import pyfolio as pf
import datetime
import os

import const
import utils

def get_bond_fund():
    fname = u'%s/债券型基金列表.xlsx'%(const.DATA_DIR)
    df = pd.read_excel(fname)
    return df

def filter_bond(df):
    # 发行时间不低于三个月
    today = datetime.datetime.today()
    df = df[today - df['issue_date'] > datetime.timedelta(90)]
    # 剔除非A类份额(包含A或者不包含任何字母)
    df = df[(df['sec_name'].str.contains('A')) | (~df['sec_name'].str.contains(r'[A-Z]'))]
    # 基金状态为开放申购|开放赎回
    df = df[df['fund_status'] == u'开放申购|开放赎回']
    return df

def save_bond_fund_panel():
    df = get_bond_fund()
    df = filter_bond(df)

    # 原始基金数据
    dic = {}
    for ticker in df['wind_code']:
        fname = '%s/history/%s.xlsx'%(const.DATA_DIR, ticker)
        df = pd.read_excel(fname, index_col=0)
        df = df[df.index >= '2014-01-01']
        if df.ix[-1, 'nav_adj'] < 0:
            print('error on %s'%(ticker))
            continue
        dic[ticker] = df
    pnl = pd.Panel(dic)

    for item in pnl.minor_axis:
        if item.endswith('return'):
            print(item)
            df = pnl.minor_xs(item)
            df.to_pickle('%s/bond_%s.pkl'%(const.FOF_DIR, item))

    # pnl.to_pickle('%s/bond.pkl'%(const.FOF_DIR))

def main():
    save_bond_fund_panel()
    # df = get_bond_fund()
    # utils.get_historical_return(df['wind_code'].tolist())

if __name__ == '__main__':
    main()
