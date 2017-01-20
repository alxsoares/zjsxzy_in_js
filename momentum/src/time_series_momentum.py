"""
This program backtests time series momentum strategy for contracts.
Metric is Sharpe ratio and max drawdown.
"""

import pandas as pd
import numpy as np
from WindPy import w
import argparse
from datetime import datetime

import show
import utils
import data
import momentum_signal

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", help="contract id", default="000300.SH", type=str)
    parser.add_argument("--look_back", help="month of lookback", default=12, type=int)
    parser.add_argument("--all", help="run all contracts(y/n)", default='n', type=str)
    parser.add_argument("--risk_free", help="risk free rate; if it equals -1, use money fund instead", default=0, type=float)
    parser.add_argument("--plot", help="plot result or not(y/n)", default='y', type=str)
    parser.add_argument("--momentum", help="type of momentum(MOP/average)", default='average', type=str)
    parser.add_argument("--s", help="start time of strategy", default="2010-01-01", type=str)
    parser.add_argument("--e", help="end time of strategy", default=datetime.now().strftime("%Y-%m-%d"), type=str)
    parser.add_argument("--volatility", help="user volatility scaling or not(y/n)", default='n', type=str)
    parser.add_argument("--period", help="rebalance period", default="daily", type=str)
    args = parser.parse_args()
    args.volatility = False if args.volatility == 'n' else True
    args.plot = False if args.plot == 'n' else True
    args.all = False if args.all == 'n' else True
    return args

def tsmom_strategy(dataframe, contract, target_vol=0.4, look_back=12,
                risk_free_rate=0, momentum="average", volatility_scaling=False,
                period="monthly", output="result.csv"):
    """
    time series momentum strategy

    input
    ------------------------------
    day_return: daily return of contract
    contract: contract id
    target_vol: volatility scaling factor
    look_back: month of look back
    risk_free_rate: risk free rate
    momentum: type of momentum to use
    volatility_scaling: use volatility scaling or not

    output
    ------------------------------
    return: daily return of the strategy
    """

    money_fund_flag = False
    if risk_free_rate == -1.0:
        money_fund_flag = True
        money_fund = data.get_money_fund()
        security = money_fund.columns[0]
        money_fund[security] = money_fund[security].pct_change()
        money_cum = (1 + money_fund[security]).cumprod()
        money_cum[0] = 1
        if period == "monthly" or period == "weekly":
            resample_period = utils.period2resample_period(period)
            money_cum = money_cum.resample(resample_period).last().ffill()
        money_cum = money_cum.pct_change(look_back)

    # get daily return of a contract
    day_return = utils.get_daily_return(dataframe, contract)
    day_return.dropna(inplace=True)

    # generate momentum signal
    if momentum == "average":
        df = momentum_signal.average_momentum(day_return, look_back=look_back, period=period)
    elif momentum == "MOP":
        df = momentum_signal.MOP_momentum(day_return, look_back=look_back, period=period)
    elif momentum == "lstm":
        df = momentum_signal.lstm_momentum(day_return, look_back=look_back, period=period)
    else:
        print("momentum type error!")

    # backtest strategy
    df["pnl"] = 0.0
    df["acc"] = 1.0
    out_df = pd.DataFrame(columns=["date", "value", "return", "position", "str_return", "acc_return"], index=df.index)
    for k, v in enumerate(df["momentum"]):
        date = df.index[k]
        out_df["date"].iloc[k] = date.strftime("%Y-%m-%d")
        out_df["value"].iloc[k] = df[contract].iloc[k]
        if k > 0:
            out_df["return"].iloc[k] = df[contract].iloc[k] / df[contract].iloc[k - 1] - 1

        if k <= look_back:
            continue

        if money_fund_flag:
            if date in money_cum.index:
                risk_free_rate = money_cum[date]
            else:
                print("date not found!")
                break

        if volatility_scaling:
            if df["momentum"].iloc[k - 1] < risk_free_rate:
                df["pnl"].iloc[k] = -(df[contract].iloc[k] / df[contract].iloc[k - 1] - 1) *\
                                    target_vol / df["%s_vol"%(contract)].iloc[k - 1] # size of position
            elif df["momentum"].iloc[k - 1] > risk_free_rate:
                df["pnl"].iloc[k] = (df[contract].iloc[k] / df[contract].iloc[k - 1] - 1) *\
                                    target_vol / df["%s_vol"%(contract)].iloc[k - 1] # size of position
        else:
            if df["momentum"].iloc[k - 1] < risk_free_rate:
                df["pnl"].iloc[k] = -(df[contract].iloc[k] / df[contract].iloc[k - 1] - 1)
            elif df["momentum"].iloc[k - 1] > risk_free_rate:
                df["pnl"].iloc[k] = (df[contract].iloc[k] / df[contract].iloc[k - 1] - 1)

        if k > 0:
            df["acc"].iloc[k] = df["acc"].iloc[k - 1] * (1 + df["pnl"].iloc[k])

        out_df["position"].iloc[k] = 1 if df["momentum"].iloc[k] > risk_free_rate else -1
        out_df["str_return"].iloc[k] = df["pnl"].iloc[k]
        out_df["acc_return"].iloc[k] = df["acc"].iloc[k]
        # print df.index[k], df["momentum"].iloc[k - 1], df[contract].iloc[k] / df[contract].iloc[k - 1] - 1, df["pnl"].iloc[k]
        yesterday = date

    out_df.to_csv(output, index=False)
    return df["pnl"]

def backtest(df, contract, look_back, risk_free_rate, momentum="average",
            volatility_scaling=False, period="monthly"):
    # get daily return of a contract
    day_return = utils.get_daily_return(df, contract)
    day_return.dropna(inplace=True)

    # get sharpe_ratio and max_drawdown of the strategy
    daily_return = tsmom_strategy(day_return, contract, target_vol=0.4, look_back=look_back,
                                risk_free_rate=risk_free_rate, momentum=momentum,
                                volatility_scaling=volatility_scaling, period=period)
    return daily_return

def run_single(contract, beginTime, endTime, look_back,
            risk_free_rate=0, plot=False, momentum="average",
            volatility_scaling=False, period="monthly"):
    # get contract data though wind API
    df = data.get_contract_data(contract, beginTime, endTime)
    benchmark = df.copy()

    # get sharpe_ratio and max_drawdown of the strategy
    daily_return = tsmom_strategy(df, contract, target_vol=0.4, look_back=look_back,
                                risk_free_rate=risk_free_rate, momentum=momentum,
                                volatility_scaling=volatility_scaling, period=period)

    benchmark = benchmark[contract].pct_change()
    start_plot_date = daily_return.index[0]
    end_plot_date = daily_return.index[-1]
    benchmark_daily_return = benchmark[(benchmark.index >= start_plot_date) & (benchmark.index <= end_plot_date)]

    # show the result
    if plot == True:
        show.show_result(daily_return=daily_return, period=period,
                        benchmark_daily_return=benchmark_daily_return, benchmark_title=contract)

def run_all(look_back, risk_free_rate=0, momentum="average"):
    df = pd.read_csv("../data/contract_01.csv")
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df.set_index('Date', inplace=True)
    ret_dict = {"Contract": [], "Sharpe": [], "Max Drawdown": [],
                "Annual Return": [], "Annual Volatility": [], "Total Return": []}
    for col in df.columns:
        con_df = df[[col]]
        daily_return = backtest(con_df, col, look_back, risk_free_rate)
        sharpe_ratio, max_drawdown, annual_return, annual_volatility, total_return = utils.metrics(daily_return, period=period)
        ret_dict["Contract"].append(col)
        ret_dict["Sharpe"].append(sharpe_ratio)
        ret_dict["Max Drawdown"].append(max_drawdown)
        ret_dict["Annual Return"].append(annual_return)
        ret_dict["Annual Volatility"].append(annual_volatility)
        ret_dict["Total Return"].append(total_return)
        print("Contract Name: %s"%(col))
    df = pd.DataFrame(ret_dict)
    df.to_csv("../data/contract_stats.csv", index=False)

if __name__ == "__main__":
    args = get_args()
    if not args.all:
        run_single(args.contract, args.s, args.e, look_back=args.look_back, risk_free_rate=args.risk_free,
                plot=args.plot, momentum=args.momentum, volatility_scaling=args.volatility, period=args.period)
    elif args.all:
        run_all(look_back=args.look_back, risk_free_rate=args.risk_free)
