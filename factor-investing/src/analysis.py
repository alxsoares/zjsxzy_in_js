# encoding: utf-8

import pandas as pd
import numpy as np
import json
import sys
from sklearn.metrics import mutual_info_score

import factors
import data
import const

with open(const.COEF_FILE, 'r') as f:
    coef = json.load(f)

def roll(df, w):
    """
    This fucntion comes from:
    http://stackoverflow.com/questions/37486502/why-does-pandas-rolling-use-single-dimension-ndarray/37491779#37491779
    """
    df.fillna(df.mean(), inplace=True)
    roll_array = np.dstack([df.values[i:i+w, :] for i in range(len(df.index) - w + 1)]).T
    panel = pd.Panel(roll_array,
                     items=df.index[w-1:],
                     major_axis=df.columns,
                     minor_axis=pd.Index(range(w), name='roll'))
    return panel.to_frame().unstack().T.groupby(level=0)

def spearman_correlation(df, factor):
    return df[factor].corr(df["return"], method="spearman")

def mututal_information(df, factor):
    return mutual_info_score(df["return"], df[factor])

def factor_coef(df, factor_list, method="Normal_IC"):
    """
    计算factor_list里的因子与收益率之间的相关性

    method: Normal_IC: Spearman相关性系数
            Mutual_Information: 互信息
    """
    pnl = factors.get_asset_factor_data(df, factor_list, frequency='d')
    pnl.ix[:, :, "return"] = pnl.minor_xs("close").pct_change() # 计算每日收益率
    ks = const.ks
    for factor in factor_list: # 枚举因子
        print("Processing factor %s..."%(factor))
        factor_df = pd.DataFrame()
        for k in ks: # 枚举窗口
            for item in pnl.items:
                print("Window size: %d\tSymbol: %s"%(k, item))
                pnl.ix[:, :, "corr"] = np.nan
                pnl.ix[:, :, factor] = pnl.minor_xs(factor).shift(1) # 用因子的当期值预测下期收益率
                factor_return_df = pnl.ix[:, :, [factor, "return"]][item]
                rolled_df = roll(factor_return_df, k)
                if method == "Normal_IC":
                    pnl.ix[:, :, "corr"][item] = rolled_df.apply(lambda x: spearman_correlation(x, factor))
                elif method == "Mutual_Information":
                    pnl.ix[:, :, "corr"][item] = rolled_df.apply(lambda x: mututal_information(x, factor))
                else:
                    raise NotImplementedError
                # 计算当期因子与下期收益率之间的相关性
                # pnl.ix[:, :, "corr"][item] = pnl.minor_xs(factor).shift(1)[item].rolling(window=k).corr(pnl.minor_xs("return")[item])
            factor_df[str(k)] = pnl.minor_xs("corr").mean(axis=1)
        if method == "Normal_IC":
            factor_df.to_excel("%s/%s_Normal_IC.xlsx"%(const.DATA_DIR, factor))
        if method == "Mutual_Information":
            factor_df.to_excel("%s/%s_Mutual_Information"%(const.DATA_DIR, factor))

def main(method="Normal_IC"):
    df = factors.read_asset_set(const.STOCK_FILE)
    factor_list = ["pe_percent", "5-day return", "120-day return", "30-day average return", "30-day volatility"]
    factor_coef(df, factor_list)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(method=sys.argv[1])
    else:
        main()
