#encoding: utf-8

from WindPy import w
import pandas as pd

import utils

w.start()

def get_pe(asset_code, start_date, end_date):
    data = w.wsd(asset_code, 'pe_ttm', start_date, end_date)
    df = utils.wind2df(data)
    return df['pe_ttm']

def get_pb(asset_code, start_date, end_date):
    data = w.wsd(asset_code, 'pb_lf', start_date, end_date)
    df = utils.wind2df(data)
    return df['pb_lf']

def get_beta(asset_code, start_date, end_date):
    df = pd.read_csv("C:/Documents/workspace/zjsxzy_in_js/result/history_beta.csv")
    df.index = pd.to_datetime(df['date'], format="%Y-%m-%d")
    df.drop(['var', 'date'], axis=1, inplace=True)
    df['mean beta'] = df.mean(axis=1)
    df = df[(df.index >= start_date) & (df.index <= end_date)]

def get_dataframe(asset_code, start_date, end_date):
    tdays = w.tdays(start_date, end_date).Times
    df = pd.DataFrame(index=tdays)
    df.index.name = 'date'
    df['pe'] = get_pe(asset_code, start_date, end_date)
    df['pb'] = get_pb(asset_code, start_date, end_date) * 10
    return df
