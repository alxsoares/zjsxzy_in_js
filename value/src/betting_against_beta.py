# encoding: utf-8
# 获取index指数的所有成分股与该指数的每月beta并保存到文件

import numpy as np
import pandas as pd
import datetime
from WindPy import w

DATA_DIR = "D:/Data"

def df_preprocess(dataframe):
    dataframe.index = pd.to_datetime(dataframe['date'], format="%Y-%m-%d")
    dataframe['return'] = dataframe['close'].pct_change()
    return dataframe

def get_history_beta(index="881001.WI", start_date="2005-01-01", end_date="2016-12-31"):
    w.start()
    codes = w.wset("IndexConstituent","date=%s;windcode=%s;field=wind_code"%(end_date, index))
    codes = codes.Data[0]

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    ind_df = pd.read_csv("%s/index/%s.csv"%(DATA_DIR, index))
    ind_df = df_preprocess(ind_df)
    ind_df = ind_df[ind_df.index >= start_date]

    # 指数月度方差
    month_ind_var_df = ind_df['return'].resample('BM').var()

    df = pd.DataFrame({"var": month_ind_var_df}, index=month_ind_var_df.index)
    for code in codes:
        print("processing %s..."%(code))
        sym_df = pd.read_csv("%s/stocks/%s.csv"%(DATA_DIR, code))
        sym_df = df_preprocess(sym_df)
        sym_df = sym_df[sym_df >= start_date]
        if sym_df.shape[0] == 0:
            continue

        betas = []
        # 枚举月
        for i, date in enumerate(month_ind_var_df.index):
            stock_return = sym_df.loc[(sym_df.index.year == date.year) & (sym_df.index.month == date.month), 'return']
            index_return = ind_df.loc[(ind_df.index.year == date.year) & (ind_df.index.month == date.month), 'return']
            if stock_return.shape == index_return.shape:
                # 计算beta系数
                beta = np.cov(stock_return, index_return)[0][1] / month_ind_var_df[i]
                betas.append(beta)
            else:
                print code, date, stock_return.shape, index_return.shape
                betas.append(np.nan)
        df[code] = betas
    df['date'] = df.index
    df.to_csv("../result/history_beta.csv", index=False)

if __name__ == "__main__":
    get_history_beta()
