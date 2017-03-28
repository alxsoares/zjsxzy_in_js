# encoding: utf-8

import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import Imputer
from sklearn import linear_model

import const
import data
import momentum
import value
import defensive

def read_asset_set(fname):
    """
    读取资产列表
    """
    df = pd.read_excel(fname)
    df.set_index('code', inplace=True)
    return df

def generate_factors(codes, factors):
    """
    计算codes中所有代码的因子并输出到文件中

    factors是一个list
    """
    for code in codes:
        for factor_name in factors:
            if factor_name.endswith("-day return"):
                k = int(factor_name.split('-')[0])
                momentum.get_k_day_return(code, days=k, save2file=True)
            if factor_name == "pe_percent":
                value.get_pe_ratio(code, save2file=True)
            if factor_name.endswith("-day average return"):
                k = int(factor_name.split("-")[0])
                momentum.get_k_day_average_return(code, days=k, save2file=True)
            if factor_name.endswith("-day volatility"):
                k = int(factor_name.split("-")[0])
                defensive.get_k_day_volatility(code, days=k, save2file=True)

def update_frequency_factor_data(asset_df, frequency='m'):
    """
    把因子数据按frequency提取出来并保存，为了提升速度
    """
    codes = asset_df.index
    for code in codes:
        fname = data.get_factor_filename(code, frequency='d')
        temp = data.read_data(fname)
        if frequency == "m":
            temp = temp.resample('M').last()
        if frequency == "y":
            temp = temp.resample('A').last()

        fname = data.get_factor_filename(code, frequency=frequency)
        temp.to_excel(fname)

def get_asset_factor_data(asset_df, factors, frequency='m'):
    """
    得到资产的价格与因子数据

    frequency: m/y
    """
    print("getting asset factor data...")
    codes = asset_df.index
    dic = {}
    for code in codes:
        fname = data.get_factor_filename(code, frequency=frequency)
        temp = data.read_data(fname)
        temp = temp[factors + ["close"]]
        dic[code] = temp
    pnl = pd.Panel(dic)
    return pnl
    
def get_score_return(pnl, factors, weights, n_groups=5):
    """
    用打分法筛选因子，并返回预测
    """
    print("getting score return")
    weights = np.array(weights) * 1.0 / sum(weights) # 标准化weights
    every_group = np.ceil(len(pnl.items) * 1.0 / n_groups) # 每组资产个数
    with open(const.COEF_FILE, 'r') as f:
        coef = json.load(f)
    pnl.ix[:, :, "return"] = pnl.minor_xs("close").pct_change()
    pnl.ix[:, :, "pred"] = 0
    for factor, weight in zip(factors, weights):
        pnl.ix[:, :, factor] = pnl.minor_xs(factor).shift(1) # 预测的是下期收益率
        pnl.ix[:, :, factor] *= coef[factor] # 有些因子要取负数，因为该因子越小越好
        pnl.ix[:, :, factor] = pnl.minor_xs(factor).rank(axis=1, method='max') # 因子从小到大排序，小的分在第1组，大的分在最后一组
        pnl.ix[:, :, factor] = np.ceil((pnl.minor_xs(factor)-1)/every_group) # 分组，组号就是其分数
        pnl.ix[:, :, factor] *= weight # 乘以因子的权重
        pnl.ix[:, :, "pred"] += pnl.minor_xs(factor)
    return pnl

def get_predict_return(pnl, factors, train_date="2010-01-01", test_date="2014-01-01"):
    """
    用回归法在训练集上训练因子模型，并返回测试集的预测结果
    """
    # 得到收益率
    print("getting predict return...")
    pnl.ix[:, :, "return"] = pnl.minor_xs("close").pct_change()
    codes = pnl.items
    dic = {}
    for code in codes:
        df = pnl.ix[code]
        df[factors] = df[factors].shift(1)
        df = df[df.index >= train_date]
        # 切分train和test
        train_df, test_df = df[df.index <= test_date], df[df.index >= test_date]
        x_train, y_train = train_df[factors][1:], train_df["return"][1:]
        x_test, y_test = test_df[factors], test_df["return"]

        # 填补NaN
        imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
        imp.fit(x_train)
        x_train, x_test = imp.transform(x_train), imp.transform(x_test)

        # 训练模型
        lr = linear_model.LinearRegression()
        lr.fit(x_train, y_train)
        print code, lr.coef_

        # 预测
        pred_test = lr.predict(x_test)
        test_df["pred"] = pred_test

        dic[code] = test_df
    pnl = pd.Panel(dic)
    return pnl

def get_group_return(pred_pnl, n_groups=5):
    """
    从预测的因子收益率，得到每组实际收益率
    """
    every_group = np.ceil(len(pred_pnl.items) * 1.0 / n_groups) # 每组资产个数

    group_df = pd.DataFrame(columns=range(1, n_groups+1))
    pred_pnl.ix[:, :, "rank"] = np.ceil((pred_pnl.minor_xs("pred").rank(axis=1, method='max')-1)/every_group) # 得到每类资产的编号
    pred_pnl.ix[:, :, "rank"][pred_pnl.ix[:, :, "rank"] == 0] = 1 # 编号为0的直接归入第一组，因为前一步候原rank为1的元素减1滞后为0
    for date in pred_pnl.major_axis:
        current_return = pred_pnl.major_xs(date).transpose().groupby("rank")["return"].mean() # 分组并得到组内平均收益
        current_return.name = date
        group_df = group_df.append(current_return)
    group_df.sort_index(inplace=True)
    return group_df

if __name__ == "__main__":
    df = read_asset_set(const.STOCK_FILE)
    codes = df.index
    for code in codes:
        data.download_data(code)
    with open(const.COEF_FILE, 'r') as f:
        coef = json.load(f)
    factors = coef.keys()
    print factors
    # factors = ["30-day volatility"]
    # weights = [1]
    codes = df.index.tolist()
    generate_factors(codes, factors)
    update_frequency_factor_data(df, frequency='m')
    # pnl = get_asset_factor_data(df, factors, frequency='m')
    # pnl = get_predict_return(pnl, factors)
    # pnl = get_score_return(pnl, factors, weights)
    # group_df = get_group_return(pnl, factors)
    # group_df.to_excel("groups.xlsx")
