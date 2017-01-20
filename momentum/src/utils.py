import pyfolio as pf

def period2resample_period(period):
    if period == "monthly":
        return "BM"
    elif period == "weekly":
        return "W"

def get_daily_return(df, contract):
    """
    get daily return from DataFrame

    input
    --------------------------
    df: dataframe of a security
    contract: name of a security

    output
    --------------------------
    return: series of daily return of a security
    """
    df.loc[:, contract] = df.loc[:, contract].pct_change()
    return df[contract]

def metrics(daily_return, period="monthly"):
    """
    return Sharpe ratio and max drawdown from daily return

    input
    --------------------------
    daily_return: daily return of strategy

    ouput
    --------------------------
    return: (sharpe_ratio, max_drawdown, annual_return, annual_volatility, total_return)
    """
    sharpe_ratio = pf.empyrical.sharpe_ratio(daily_return, period=period)
    max_drawdown = pf.empyrical.max_drawdown(daily_return)
    annual_return = pf.empyrical.annual_return(daily_return, period=period)
    annual_volatility = pf.empyrical.annual_volatility(daily_return, period=period)
    total_return = (1 + daily_return).cumprod().ix[-1]
    return sharpe_ratio, max_drawdown, annual_return, annual_volatility, total_return - 1
