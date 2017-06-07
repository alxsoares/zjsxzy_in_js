# encoding: utf-8

import pandas as pd
import datetime
from WindPy import w
import os

import utils
import const
import stock_fund
import bond_fund
import mixed_fund

rptDate = '20161231'

def update_fund_list(df, fname):
    df[['sec_name', 'wind_code']].to_excel(fname, index=False)
    df = pd.read_excel(fname)
    # 基金二级分类
    data = w.wss(df['wind_code'].tolist(), "fund_investtype")
    temp = utils.wind2df(data)
    df['investtype'] = temp['fund_investtype']
    # 发行时间
    data = w.wss(df['wind_code'].tolist(), "issue_date")
    temp = utils.wind2df(data)
    df['issue_date'] = temp['issue_date']
    # 资产净值
    data = w.wss(df['wind_code'].tolist(), "prt_netasset","rptDate=%s"%(rptDate))
    temp = utils.wind2df(data)
    df['netasset'] = temp['prt_netasset']
    # 基金经理
    data = w.wss(df['wind_code'].tolist(), "fund_fundmanager")
    temp = utils.wind2df(data)
    df['fundmanager'] = temp['fund_fundmanager']
    # 当前申购赎回状态
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    data = w.wss(df['wind_code'].tolist(), "fund_dq_status","tradeDate=%s"%(today))
    temp = utils.wind2df(data)
    df['fund_status'] = temp['fund_dq_status']
    df.to_excel(fname, index=False)

def update_stock_list():
    w.start()
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    data = w.wset("sectorconstituent","date=%s;windcode=885012.WI"%(today))
    df = utils.wind2df(data)
    fname = u'%s/股票型基金列表.xlsx'%(const.DATA_DIR)
    update_fund_list(df, fname)

def update_bond_list():
    w.start()
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    data = w.wset("sectorconstituent","date=%s;windcode=885005.WI"%(today))
    df = utils.wind2df(data)
    fname = u'%s/债券型基金列表.xlsx'%(const.DATA_DIR)
    update_fund_list(df, fname)

def update_mixed_list():
    w.start()
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    data = w.wset("sectorconstituent","date=%s;windcode=885013.WI"%(today))
    df = utils.wind2df(data)
    fname = u'%s/混合型基金列表.xlsx'%(const.DATA_DIR)
    update_fund_list(df, fname)

def update_nav(ticker):
    w.start()
    if datetime.datetime.now().hour < 15:
        today = datetime.datetime.today() - datetime.timedelta(1)
    else:
        today = datetime.datetime.today()
    fname = '%s/history/%s.xlsx'%(const.DATA_DIR, ticker)
    if not os.path.exists(fname):
        utils.down_historical_nav(ticker)
        df = pd.read_excel(fname, index_col=0)
        df = utils.get_historical_return(df)
        df.to_excel(fname)
        return
    old_df = pd.read_excel(fname, index_col=0)
    last_day = old_df.index[-1]
    days = (today - last_day).days - 1
    if days < 0:
        return
    data = w.wsd(ticker, "NAV_adj", "ED-%dD"%(days), today, "")
    df = utils.wind2df(data)
    for col in old_df.columns:
        if col not in df.columns:
            df[col] = 0
    df = old_df.append(df)
    df = utils.get_historical_return(df)
    df.to_excel(fname)

def update_bond_data():
    bond_df = bond_fund.get_bond_fund()
    for ticker in bond_df['wind_code']:
        print('updating %s...'%(ticker))
        update_nav(ticker)
    bond_fund.save_bond_fund_panel()

def update_stock_data():
    stock_df = stock_fund.get_stock_fund()
    for ticker in stock_df['wind_code']:
        print('updating %s...'%(ticker))
        update_nav(ticker)
    stock_fund.save_stock_fund_panel()

def update_mixed_data():
    mixe_df = mixed_fund.get_mixed_fund()
    for ticker in mixe_df['wind_code']:
        print('updating %s...'%(ticker))
        update_nav(ticker)
    mixed_fund.save_mixed_fund_panel()

if __name__ == '__main__':
    update_bond_data()
    update_stock_data()
    update_mixed_data()
    # update_stock_list()
    # update_bond_list()
    # update_mixed_list()
    # update_nav('150094.OF')
