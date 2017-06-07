# encoding: utf-8

import pandas as pd
import numpy as np

import volatility
import const

def get_dataframe(asset1, asset2):
    df1 = volatility.get_dataframe(asset1)
    df2 = volatility.get_dataframe(asset2)
    df1['cor'] = df1['vol'].rolling(window=const.window).corr(df2['vol'])
    return pd.DataFrame({'cor': df1['cor']}, index=df1.index)

def rank_percentile(array):
    """
    返回s的最后一个元素在s中的分位值
    """
    s = pd.Series(array)
    s = s.rank(pct=True)
    return s.iloc[-1]

def all_mean():
    assets = const.NAMES.keys()
    df = pd.DataFrame({}, index=assets, columns=assets)
    for i, asset1 in enumerate(assets):
        for j, asset2 in enumerate(assets):
            if i == j:
                val = np.nan
            elif i < j:
                df1 = volatility.get_dataframe(asset1)
                df2 = volatility.get_dataframe(asset2)
                corrs = df1['vol'].rolling(window=const.window).corr(df2['vol'])
                val = rank_percentile(corrs)
            else:
                df1 = volatility.get_dataframe(asset1)
                df2 = volatility.get_dataframe(asset2)
                val = df1['vol'][-const.window:].corr(df2['vol'][-const.window:], method='pearson')
            df.loc[asset1, asset2] = val
    df.to_excel("%s/correlation.xlsx"%(const.DATA_DIR), float_format='%.2f')

def merge_to_one_excel():
    assets = const.NAMES.keys()
    res = pd.DataFrame()
    for asset in assets:
        df = volatility.get_dataframe(asset)
        res[asset] = df['vol']
    print res.head()
    res.to_excel('%s/vix.xlsx'%(const.DATA_DIR), float_format='%.2f')

if __name__ == '__main__':
    # df = get_dataframe('VXEEM', 'VXFXI')
    # print df.tail()
    all_mean()
    merge_to_one_excel()
