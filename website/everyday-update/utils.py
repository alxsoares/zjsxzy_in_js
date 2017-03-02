import pyfolio as pf
from WindPy import w
import numpy as np
import pandas as pd

w.start()

def wind2df(raw_data):
    dic = {}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[str(field.lower())] = data
    return pd.DataFrame(dic, index=raw_data.Times)

def get_money_fund_daily_return(start_date, end_date):
    code = "H11025.CSI"
    data = w.wsd(code, 'close', start_date, end_date)
    df = wind2df(data)
    df['return'] = df['close'].pct_change()
    return df['return'].dropna()

def get_sharpe_ratio(daily_return):
    # sharpe_ratio = pf.empyrical.sharpe_ratio(daily_return)
    start_date = daily_return.index[0]
    end_date = daily_return.index[-1]
    days = int((end_date - start_date).days)
    acc_return = (1 + daily_return).cumprod()[-1]

    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    money_daily_return = get_money_fund_daily_return(start_date, end_date)
    money_acc_return = (1 + money_daily_return).cumprod()[-1]

    volatility = daily_return.std() * np.sqrt(243)

    sharpe_ratio = (acc_return**(365./days) - money_acc_return**(365./days)) / volatility
    return sharpe_ratio
