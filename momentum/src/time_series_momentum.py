"""
This program backtests time series momentum strategy for contracts.
Metric is Sharpe ratio and max drawdown.
"""

import pandas as pd
import numpy as np
from WindPy import w
from datetime import datetime
import show
import utils
import data
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", help="contract id", default="IF00.CFE", type=str)
    parser.add_argument("--look_back", help="month of lookback", default=12, type=int)
    parser.add_argument("--all", help="run all contracts(y/n)", default='n', type=str)
    parser.add_argument("--risk_free", help="risk free rate; if it equals -1, use money fund instead", default=0, type=float)
    parser.add_argument("--plot", help="plot result or not(y/n)", default='n', type=str)
    parser.add_argument("--s", help="start time of strategy", default="1990-01-01", type=str)
    parser.add_argument("--e", help="end time of strategy", default=datetime.now().strftime("%Y-%m-%d"), type=str)
    args = parser.parse_args()
    return args

def tsmom_strategy(ret_m_index, contract, target_vol=0.4, look_back=12, plot=False, risk_free_rate=0):
    money_fund_flag = False
    if risk_free_rate == -1.0:
        money_fund_flag = True
        money_fund = data.get_money_fund()
        security = money_fund.columns[0]
        money_fund[security] = money_fund[security].pct_change()
        money_cum = (1 + money_fund[security]).cumprod()
        money_cum[0] = 1
        money_cum = money_cum.resample("BM").last().ffill()
        money_cum = money_cum.pct_change(look_back)

    df = ret_m_index.copy()
    df["return"] = df[contract].pct_change(look_back) # return over last look_back months
    df["pnl"] = 0.0
    for k, v in enumerate(df["return"]):
        if k <= look_back:
            continue

        if money_fund_flag:
            date = df.index[k]
            if date in money_cum.index:
                risk_free_rate = money_cum[date]
            else:
                print("date not found!")

        if df["return"].iloc[k - 1] < risk_free_rate:
            df["pnl"].iloc[k] = (df[contract].iloc[k - 1] / df[contract].iloc[k] - 1) *\
                                target_vol / df["%s_vol"%(contract)].iloc[k - 1] # size of position
        elif df["return"].iloc[k - 1] > risk_free_rate:
            df["pnl"].iloc[k] = (df[contract].iloc[k] / df[contract].iloc[k - 1] - 1) *\
                                target_vol / df["%s_vol"%(contract)].iloc[k - 1] # size of position
    return df["pnl"]

def backtest(df, contract, look_back, risk_free_rate):
    # get daily return of a contract
    day_return = utils.get_daily_return(df, contract)
    day_return.dropna(inplace=True)

    # calculate daily volatility scaling, see the formula in paper
    day_vol = day_return.ewm(ignore_na=False, adjust=True, com=60, min_periods=0).std(bias=False)
    vol = day_vol * np.sqrt(261) # annualise

    # get monthly return and volatility
    ret_index = (1 + day_return).cumprod()
    ret_index[0] = 1
    ret_index = pd.concat([ret_index, vol], axis=1)
    ret_index.columns = [contract, "%s_vol"%(contract)]
    ret_m_index = ret_index.resample('BM').last().ffill()
    ret_m_index.ix[0][contract] = 1

    # get sharpe_ratio and max_drawdown of the strategy
    daily_return = tsmom_strategy(ret_m_index, contract, target_vol=0.4, look_back=look_back, risk_free_rate=risk_free_rate)
    return daily_return

def run_single(contract, beginTime, endTime, look_back, risk_free_rate=0, plot=False):
    # get contract data though wind API
    df = data.get_contract_data(contract, beginTime, endTime)
    df["value"] = df[contract].pct_change()
    daily_return = backtest(df, contract, look_back, risk_free_rate)
    if plot == True:
        show.show_result(daily_return=daily_return, benchmark_daily_return=df["value"], benchmark_title=contract)

def run_all(look_back, risk_free_rate=0):
    df = pd.read_csv("../data/contract_01.csv")
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df.set_index('Date', inplace=True)
    ret_dict = {"Contract": [], "Sharpe": [], "Max Drawdown": []}
    for col in df.columns:
        con_df = df[[col]]
        daily_return = backtest(con_df, col, look_back, risk_free_rate)
        sharpe_ratio, max_drawdown, _, _ = utils.metrics(daily_return)
        ret_dict["Contract"].append(col)
        ret_dict["Sharpe"].append(sharpe_ratio)
        ret_dict["Max Drawdown"].append(max_drawdown)
        print("Contract Name: %s"%(col))
        print("Sharpe Ratio = " + str(sharpe_ratio))
        print("Max Drawdown = " + str(max_drawdown))
    df = pd.DataFrame(ret_dict)
    df.to_csv("../data/contract_stats.csv", index=False)

if __name__ == "__main__":
    args = get_args()
    if args.all == 'n':
        if args.plot == 'y':
            run_single(args.contract, args.s, args.e, look_back=args.look_back, risk_free_rate=args.risk_free, plot=True)
        else:
            run_single(args.contract, args.s, args.e, look_back=args.look_back, risk_free_rate=args.risk_free)
    elif args.all == 'y':
        run_all(look_back=args.look_back, risk_free_rate=args.risk_free)
