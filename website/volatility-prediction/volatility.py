# encoding: utf-8

from WindPy import w
import pandas as pd
import numpy as np
import datetime
import os
from sklearn import linear_model
from sklearn.kernel_ridge import KernelRidge
from sklearn.svm import SVR
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor

import word
import utils

DATA_WORD_DIR = "C:/Users/jgtzsx01/Documents/workspace/data/wallstreetcn_words"
w.start()

def get_data(asset, start_date, end_date):
    data = w.wsd(asset, 'close', beginTime=start_date, endTime=end_date)
    df = utils.wind2df(data)
    return df

def get_PE(start_date, end_date):
    """
    return pandas series
    """
    WIND_CODE = "881001.WI"
    data = w.wsd(WIND_CODE, 'pe_ttm', beginTime=start_date, endTime=end_date)
    pe_df = utils.wind2df(data)
    return pe_df['pe_ttm']

def get_ytm(start_date, end_date):
    BOND_CODE = "065.CS"
    data = w.wsd(BOND_CODE, 'ytm_b', start_date, end_date, "returnType=1")
    ytm_df = utils.wind2df(data)
    return (1 / ytm_df['ytm_b'])

def get_jpy(start_date, end_date):
    JPYCNY_CODE = "JPYCNY.EX"
    data = w.wsd(JPYCNY_CODE, 'close', beginTime=start_date, endTime=end_date)
    jpy_df = utils.wind2df(data)
    return jpy_df['close']

def get_vix(start_date, end_date):
    VIX_CODE = "000188.SH"
    data = w.wsd(VIX_CODE, 'close', beginTime=start_date, endTime=end_date)
    vix_df = utils.wind2df(data)
    return vix_df['close']

def get_word(key_word):
    fname = unicode("%s/%s.csv"%(DATA_WORD_DIR, key_word))
    if not os.path.exists(fname):
        word.main(key_word)
    word_df = pd.read_csv(fname)
    word_df['date'] = pd.to_datetime(word_df['date'], format="%Y-%m-%d")
    word_df.set_index('date', inplace=True)
    word_df.sort_index(inplace=True)
    return word_df['value']

def train_test_model(vol_df, short_term_days, features, model, train_date, test_date):
    predX = vol_df.ix[-short_term_days-1:, features]
    pred_end_date = w.tdaysoffset(short_term_days, predX.index[-1]).Data[0][0]
    pred_dates = w.tdays(predX.index[-1].strftime("%Y-%m-%d"), pred_end_date.strftime("%Y-%m-%d")).Times
    predX.index = pred_dates

    vol_df[features] = vol_df[features].shift(short_term_days)
    vol_df.dropna(inplace=True)
    train_df = vol_df[vol_df.index <= test_date]
    test_df = vol_df[vol_df.index >= test_date]
    train_df = train_df.append(test_df.ix[0]) # 为了让图看上去连续
    trainX, trainY = train_df[features], train_df['vol']
    testX, testY = test_df[features], test_df['vol']

    # 用Lasso来做feature selection
    lasso = linear_model.Lasso(alpha=0.0005)
    lasso.fit(trainX, trainY)
    sfm = SelectFromModel(lasso, prefit=True)
    fea_trainX = sfm.transform(trainX)
    fea_testX = sfm.transform(testX)
    fea_predX = sfm.transform(predX)

    if model == "LinearRegression":
        reg_model = linear_model.LinearRegression()
    elif model == "KernelRidgeRegression":
        reg_model = KernelRidge(kernel='rbf')
    elif model == "SupportVectorRegression":
        reg_model = SVR(kernel="linear")
    elif model == "Ridge":
        reg_model = linear_model.Ridge()
    elif model == "RandomForestRegression":
        reg_model = RandomForestRegressor()
    elif model == "AdaBoostRegression":
        reg_model = AdaBoostRegressor()
    else:
        return NotImplementedError

    reg_model.fit(fea_trainX, trainY)
    train_pred = reg_model.predict(fea_trainX)
    test_pred = reg_model.predict(fea_testX)
    pred_pred = reg_model.predict(fea_predX)
    return (pd.DataFrame({'pred': train_pred}, index=trainX.index),
            pd.DataFrame({'pred': test_pred}, index=testX.index),
            pd.DataFrame({'pred': pred_pred}, index=predX.index))

def get_volatility(asset,
                   key_word,
                   model='LinearRegression',
                   short_term_days=63,
                   long_term_days=490,
                   train_date="2000-01-01",
                   test_date="2017-01-01",
                   start_date="2000-01-01",
                   end_date=(datetime.datetime.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")):

    df = get_data(asset, start_date, end_date)
    # 每日收益率
    df['return'] = df['close'].pct_change()
    df.dropna(inplace=True)
    # 年化日波动率
    volatility = df['return'].rolling(window=short_term_days).std() * np.sqrt(243)
    volatility.name = 'vol'
    vol_df = pd.DataFrame(volatility)
    # 获取数据
    # features = ['short-term vol', 'long-term vol', 'pe', 'ytm', 'jpycny', 'vix']
    features = []
    # 1. 短周期波动率
    # vol_df['short-term vol'] = vol_df['vol']
    for k in range(7, short_term_days+1):
        feature_name = "%d-day short-term vol"%(k)
        features.append(feature_name)
        vol_df[feature_name] = df['return'].rolling(window=k).std() * np.sqrt(243)
    # 2. 长周期波动率
    # volatility = df['return'].rolling(window=long_term_days).std() * np.sqrt(243)
    # vol_df['long-term vol'] = volatility
    for k in range(243, long_term_days+1):
        feature_name = "%d-day short-term vol"%(k)
        features.append(feature_name)
        vol_df[feature_name] = df['return'].rolling(window=k).std() * np.sqrt(243)
    # 3. 万德全A PE
    pe_value = get_PE(start_date, end_date)
    features.append("pe")
    vol_df['pe'] = pe_value
    # 4. 中债指数收益率的倒数
    ytm_value = get_ytm(start_date, end_date)
    features.append("ytm")
    vol_df['ytm'] = ytm_value
    # 5. 日元兑人民币短周期波动率
    jpy_value = get_jpy(start_date, end_date)
    features.append("jpycny")
    vol_df['jpycny'] = jpy_value
    # 6. 中国波动率指数
    vix_value = get_vix(start_date, end_date)
    features.append('vix')
    vol_df['vix'] = vix_value
    # 7. 过去7天词频
    word_value = get_word(key_word)
    vol_df['word'] = 0
    for ind in vol_df.index:
        word_ind = ind.strftime("%Y-%m-%d")
        word_ind = pd.to_datetime(word_ind, format="%Y-%m-%d")
        if word_ind in word_value.index:
            vol_df.ix[ind, 'word'] = word_value[word_ind]
    features.append('word')
    vol_df['word'] = vol_df['word'].rolling(window=7).sum()

    # 训练并预测
    vol_df.dropna(inplace=True)
    vol_df = vol_df[vol_df.index >= train_date]
    train_df, test_df, pred_df = train_test_model(vol_df, short_term_days, features, model, train_date, test_date)

    return vol_df, train_df, test_df, pred_df
