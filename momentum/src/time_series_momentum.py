"""
This program backtests time series momentum strategy for single contract.
Metric is Sharpe ratio and max drawdown.

Example:
python time_series_momentum.py IF00.CFE
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import datetime
import seaborn as sns
import pyfolio as pf
from WindPy import w
import sys

w.start()

def daily_return(df, contract):
    df[contract] = df["close"].pct_change()
    return df[contract]

def preprocess(contract):
    raw = w.wsd(contract, "open,high,low,close,volume,amt", beginTime="2002-01-01", endTime="2017-01-17")
    dic = {}
    for data, field in zip(raw.Data, raw.Fields):
        dic[str.lower(str(field))] = data
    df = pd.DataFrame(dic, index=raw.Times)
    return df

def tsmom_strategy(ret_m_index, contract, target_vol=0.4, look_back=12, plot=False, risk_free_rate=0):
    std_index = ret_m_index.index
    pnl = pd.DataFrame(index=std_index)
    leverage = pd.DataFrame(index=std_index)
    df = ret_m_index.copy()
    df["return"] = df[contract].pct_change(look_back) # return over last look_back months
    df["pnl"] = 0.0
    for k, v in enumerate(df["return"]):
        if k <= look_back:
            continue
        if df["return"].iloc[k - 1] < risk_free_rate:
            df["pnl"].iloc[k] = (df[contract].iloc[k - 1] / df[contract].iloc[k] - 1) *\
                                target_vol / df["%s_vol"%(contract)].iloc[k - 1] # size of position
        elif df["return"].iloc[k - 1] > risk_free_rate:
            df["pnl"].iloc[k] = (df[contract].iloc[k] / df[contract].iloc[k - 1] - 1) *\
                                target_vol / df["%s_vol"%(contract)].iloc[k - 1] # size of position
        # print k, df["pnl"].iloc[k]
    pnl = pd.concat([pnl, df["pnl"]], axis=1)
    df = pnl
    df['port_avg'] = df.mean(skipna = 1, axis=1)

    sharpe_ratio = pf.empyrical.sharpe_ratio(df["port_avg"], period="monthly")
    max_drawdown = pf.empyrical.max_drawdown(df["port_avg"])
    print("Sharpe Ratio = " + str(sharpe_ratio))
    print("Max Drawdown = " + str(max_drawdown))
    if plot == True:
        pf.plot_drawdown_underwater(df["port_avg"])
    return sharpe_ratio, max_drawdown

def main(contract):
    df = preprocess(contract)
    day_return = daily_return(df, contract)
    day_return.dropna(inplace=True)

    # calculate volatility scaling
    day_vol = day_return.ewm(ignore_na=False, adjust=True, com=60, min_periods=0).std(bias=False)
    vol = day_vol * np.sqrt(261) # annualise

    # get monthly return
    std_index = day_return.resample("BM").last() # month index
    ret_index = (1 + day_return).cumprod()
    ret_index[0] = 1
    ret_index = pd.concat([ret_index, vol], axis=1)
    ret_index.columns = [contract, "%s_vol"%(contract)]
    ret_m_index = ret_index.resample('BM').last().ffill()
    ret_m_index.ix[0][contract] = 1
    origin_shapre_ratio = pf.empyrical.sharpe_ratio(ret_m_index[contract].pct_change(), period="monthly")
    origin_max_drawdown = pf.empyrical.max_drawdown(ret_m_index[contract].pct_change())
    print("Origin Sharpe Ratio = " + str(origin_shapre_ratio))
    print("Origin Max Drawdown = " + str(origin_max_drawdown))
    sharpe_ratio, max_drawdown = tsmom_strategy(ret_m_index, contract, target_vol=0.4, look_back=12)

if __name__ == "__main__":
    main(sys.argv[1])
