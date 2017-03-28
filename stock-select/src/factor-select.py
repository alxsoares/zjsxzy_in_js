# encoding: utf-8-

import pandas as pd
import numpy as np
from WindPy import w
import datetime

import momentum
import hurst
import utils

CODE_FILE = "C:/Users/jgtzsx01/Documents/workspace/data/index-component/000300.xlsx"
DATA_DIR = "C:\Users\jgtzsx01\Documents\workspace\data\stocks"

def wind2df(raw_data):
    """
    把wind数据转换成dataframe
    """
    dic = {}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[str(field.lower())] = data
    return pd.DataFrame(dic, index=raw_data.Times)

def download_data(codes,
                  start_date="2016-03-01",
                  end_date=datetime.datetime.today().strftime("%Y-%m-%d")):
    w.start()
    for code in codes:
        data = w.wsd(code, fields="open,close,high,low,volume", beginTime=start_date, endTime=end_date)
        df = wind2df(data)
        df.to_excel("%s/%s.xlsx"%(DATA_DIR, code))

def check_factor(codes, factor="momentum", ks=range(105, 123)):
    for k in ks:
        mom_df = pd.DataFrame(columns=codes)
        for code in codes:
            print("processing %d day return with %s"%(k, code))
            if factor == "momentum":
                df = momentum.get_k_day_return(code, k, periods=5)
            if factor == "hurst":
                df = hurst.get_k_day_hurst(code, k, periods=5)
            rolled_df = utils.roll(df, k)
            mom_df[code] = rolled_df.apply(lambda x: utils.spearman_correlation(x, factor))
        if k == ks[0]:
            res_df = pd.DataFrame(index=mom_df.index)
        res_df["%d"%(k)] = mom_df.mean(axis=1)
        res_df.to_excel("./%s.xlsx"%(factor))
    res_df.to_excel("./%s.xlsx"%(factor))


def update():
    df = pd.read_excel(CODE_FILE)
    codes = df["code"].tolist()
    download_data(codes)

if __name__ == "__main__":
    df = pd.read_excel(CODE_FILE)
    codes = df["code"].tolist()
    check_factor(codes, "hurst")
