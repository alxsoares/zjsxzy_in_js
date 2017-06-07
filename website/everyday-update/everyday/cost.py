# encoding: utf-8
# 计算个股真实换手率，用以计算其平均持有成本

import pandas as pd
import numpy as np
from scipy.stats import stats
from WindPy import w
import datetime
import os

import const
import utils

def get_codes(index_code):
    df = pd.read_excel("%s/%s.xlsx"%(const.INDEX_DIR, index_code))
    return df["code"].tolist()

def get_wind_data(code, start_date, end_date):
    w.start()
    fields = "mkt_freeshares,vwap,amt,close,dealnum,free_turn,volume,mfd_buyamt_a,mfd_sellamt_a,high,low"
    # data = w.wsd(code, fields, beginTime=start_date, endTime=end_date, "PriceAdj=F")
    # data = w.wsd("000402.SZ", "mkt_freeshares,vwap,amt,close", "2017-03-15", "2017-03-16", "PriceAdj=F")
    data = w.wsd(code, fields, start_date, end_date, "traderType=1;PriceAdj=F")
    return utils.wind2df(data)

def append_to_old_excel(code):
    """
    把最新的到今天/昨天的数据加入到旧的表格中
    """
    fname = "%s/%s.xlsx"%(const.STOCK_DIR, code)
    df = pd.read_excel(fname, index_col=0)
    '''
    w.start()
    data = w.wsd(code, 'high,low', df.index[0].strftime('%Y-%m-%d'), df.index[-1].strftime('%Y-%m-%d'), 'PriceAdj=F')
    add_df = utils.wind2df(data)
    df = pd.concat([df, add_df], axis=1)
    df.to_excel(fname)
    '''

    start_date = (df.index[-1] + datetime.timedelta(1)).strftime("%Y-%m-%d")
    if datetime.datetime.now().hour < 15:
        end_date = (datetime.datetime.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
    else:
        end_date = datetime.datetime.today().strftime("%Y-%m-%d")
    if datetime.datetime.strptime(start_date, "%Y-%m-%d") > datetime.datetime.strptime(end_date, "%Y-%m-%d"):
        return

    print("updating %s"%(code))
    add_df = get_wind_data(code, start_date, end_date)
    # print add_df
    add_df["turnover"] = add_df["amt"] / add_df["mkt_freeshares"]

    df = df.append(add_df)
    df.to_excel(fname)

def update_all(index_code=None, start_date="2014-06-01",
                     end_date=(datetime.datetime.today()-datetime.timedelta(1)).strftime("%Y-%m-%d")):
    if index_code == None:
        # 更新文件夹中所有
        codes = [f[:-5] for f in os.listdir(const.STOCK_DIR)]
    else:
        codes = get_codes(index_code)
    for code in codes:
        fname = '%s/%s.xlsx'%(const.STOCK_DIR, code)
        if os.path.exists(fname):
            append_to_old_excel(code)
        else:
            print("downloding %s..."%(code))
            df = get_wind_data(code, start_date, end_date)
            df["turnover"] = df["amt"] / df["mkt_freeshares"] # 计算换手率
            df.to_excel(fname)

def convert_cost(df, stock=None):
    """
    计算历史的成本和100%换手天数
    """
    if stock == None:
        # 产生一个新的文件
        df.loc[:, "turnover days"] = np.nan # 换手天数
        df.loc[:, "avg cost"] = np.nan # 平均持有成本
        df.loc[:, "profit percentage"] = np.nan # 盈利持仓占比
        k = 0
        dates = df.index
    else:
        # 在原有文件上增加新数据
        fname = "%s/%s"%(const.BY_STOCK_DIR, stock)
        old_df = pd.read_excel(fname, index_col=0)
        if old_df.index[-1] >= df.index[-1]:
            return old_df
        df.loc[:, "turnover days"] = old_df["turnover days"]
        df.loc[:, "avg cost"] = old_df["avg cost"]
        df.loc[:, "profit percentage"] = old_df["profit percentage"]
        if pd.isnull(old_df["turnover days"][-1]):
            k = 0
        else:
            k = int(old_df.shape[0] - old_df["turnover days"][-1])
        dates = df[df.index > old_df.index[-1]].index

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

        # (prev_index, index)这段区间里的换手率总和正好大于等于1
        temp_df = df[(df.index >= prev_index) & (df.index <= index)]
        cost = (temp_df["vwap"] * temp_df["amt"]).sum() / temp_df["amt"].sum()
        current_price = df.loc[index, 'close']
        profit_volume = temp_df[temp_df['vwap'] < current_price]['volume'].sum()
        profit_percentage = profit_volume / temp_df['volume'].sum()
        df.loc[index, "avg cost"] = cost
        # df.loc[index, "turnover days"] = (index - prev_index).days
        df.loc[index, "turnover days"] = i - k + old_df.shape[0]
        df.loc[index, "profit percentage"] = profit_percentage
    return df[["turnover days", "avg cost", "close", "profit percentage"]]

def filter_files(files, index_code):
    index_file = "%s/%s.xlsx"%(const.INDEX_DIR, index_code)
    df = pd.read_excel(index_file)
    codes = set(df["code"].tolist())
    files = [f for f in files if f[:-5] in codes]
    return files

def get_history_turnover(index_code=None):
    """
    计算所有股票的
    1. 历史平均持有成本、
    2. 100%换手天数
    3. 收盘价
    并保存到D:/Data/avg_cost/by stock
    """
    files = [f for f in os.listdir(const.STOCK_DIR) if f.endswith("xlsx")]
    if index_code != None:
        files = filter_files(files, index_code)

    for stock in files:
        print("processing %s..."%(stock))
        fname = "%s/%s"%(const.STOCK_DIR, stock)
        df = pd.read_excel(fname, index_col=0)
        if os.path.exists("%s/%s"%(const.BY_STOCK_DIR, stock)):
            df = convert_cost(df, stock)
        else:
            df = convert_cost(df)
        df.to_excel("%s/%s"%(const.BY_STOCK_DIR, stock))

def get_all_by_stock_panel(files):
    """
    给定files中的by_stock的股票历史成本与换手，得到一个综合的panel类型数据
    """
    dic = {}
    for stock in files:
        # print("processing %s..."%(stock))
        df = pd.read_excel("%s/%s"%(const.BY_STOCK_DIR, stock), index_col=0)
        df.index = pd.to_datetime(df.index)
        dic[stock[:-5]] = df
    pnl = pd.Panel(dic)
    return pnl

"""
def save_by_date(index_code=None):
    files = [f for f in os.listdir(const.BY_STOCK_DIR)]
    if index_code != None:
        files = filter_files(files, index_code)

    pnl = get_all_by_stock_panel(files)
    pnl.ix[:, :, "current return"] = (pnl.minor_xs("close") - pnl.minor_xs("avg cost")) / pnl.minor_xs("avg cost")
    pnl.ix[:, :, "rolling current return"] = pnl.minor_xs("current return").rolling(window=7).mean()

    for date in pnl.major_axis:
        df = pnl.major_xs(date).T
        df.to_excel("%s/%s.xlsx"%(const.BY_DATE_DIR, date.strftime("%Y-%m-%d")))
"""

def calculate_profit_percentage(index_code=None):
    """
    计算每只股票的盈利持仓占比
    """
    files = [f for f in os.listdir(const.BY_STOCK_DIR)]
    if index_code != None:
        files = filter_files(files, index_code)

    for stock in files:
        ticker = stock[:-5]
        fname = '%s/%s.xlsx'%(const.STOCK_DIR, ticker)
        df = pd.read_excel(fname, index_col=0)
        fname = '%s/%s.xlsx'%(const.BY_STOCK_DIR, ticker)
        cost_df = pd.read_excel(fname, index_col=0)
        df = pd.concat([df, cost_df[['turnover days', 'avg cost']]], axis=1)
        print('processing %s...'%(ticker))
        if 'profit percentage' in df.columns:
            return

        df.loc[:, 'profit percentage'] = np.nan
        for index in df.index:
            turnover_days = df.loc[index, 'turnover days']
            current_price = df.loc[index, 'close']
            if not np.isnan(turnover_days):
                start_day = index - datetime.timedelta(turnover_days)
                select_df = df[(df.index >= start_day) & (df.index <= index)]
                profit_volume = select_df[select_df['vwap'] < current_price]['volume'].sum()
                df.loc[index, 'profit percentage'] = profit_volume / select_df['volume'].sum()
        df[['turnover days', 'avg cost', 'close', 'profit percentage']].to_excel(fname)

def cal_market_cost(index_code=None):
    """
    计算市场当前的成本与盈亏情况、skewness分布
    保存结果到./data/market.xlsx
    """
    fname = "%s/%s.xlsx"%(const.DATA_DIR, index_code)
    if os.path.exists(fname):
        return
    # 读入全市场所有股票的历史换手天数、持有成本与收盘价
    files = [f for f in os.listdir(const.BY_STOCK_DIR)]
    if index_code != None:
        files = filter_files(files, index_code)

    pnl = get_all_by_stock_panel(files)
    # 计算每天的持有成本
    pnl.ix[:, :, "current return"] = (pnl.minor_xs("close") - pnl.minor_xs("avg cost")) / pnl.minor_xs("avg cost")
    # 计算滚动的持有成本
    # t = 8
    # pnl.ix[:, :, "rolling current return"] = pnl.minor_xs("current return").rolling(window=t).mean()

    dates = pnl.major_axis
    market_df = pd.DataFrame(index=dates)
    # 市场平均的换手天数
    market_df.loc[:, "turnover days"] = pnl.minor_xs("turnover days").mean(axis=1)
    # 市场平均的成本
    market_df.loc[:, "current return"] = pnl.ix[:, :, "current return"].mean(axis=1)
    # 市场平均的滚动成本
    # market_df.loc[:, "rolling current return"] = pnl.ix[:, :, "rolling current return"].mean(axis=1)
    # 市场平均盈亏占比
    market_df['profit percentage'] = pnl.ix[:, :, 'profit percentage'].mean(axis=1)
    # 市场kurtosis, kewness
    """
    market_df["skewness"] = np.nan
    market_df["kurtosis"] = np.nan
    for date in dates:
        d = pnl.major_xs(date).ix["turnover days"].dropna()
        if d.shape[0] >= 400:
            skewness = stats.skew(d)
            kurtosis = stats.kurtosis(d)
            market_df.loc[date, "skewness"] = skewness
            market_df.loc[date, "kurtosis"] = kurtosis
    """
    market_df.to_excel(fname)
    return market_df

def delete_old_files():
    files = [f for f in os.listdir(const.DATA_DIR) if f.endswith('.csv')]
    for f in files:
        fname = '%s/%s'%(const.DATA_DIR, f)
        os.remove(fname)

def main():
    # update_all("881001")
    # delete_old_files()
    get_history_turnover()
    os.remove('%s/881001.xlsx'%(const.DATA_DIR))
    cal_market_cost('881001')

if __name__ == "__main__":
    main()
