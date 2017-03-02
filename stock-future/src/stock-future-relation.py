# encoding: utf-8
import pandas as pd
import numpy as np
import os
import datetime
import argparse

import utils

STOCKS_DIR = "C:/Users/jgtzsx01/Documents/workspace/data/stocks"
FUTURE_DIR = "C:/Users/jgtzsx01/Documents/workspace/zjsxzy_in_js/data"
NAME = "有色金属"
# NAME = "煤炭"
# NAME = "石油石化"
# NAME = "钢铁"
# NAME = "农林牧渔"
COMPONENT_FILE = "%s/%s.csv"%(FUTURE_DIR, NAME)
FUTURE_LIST = "AU01.SHF,AG01.SHF,CU01.SHF,SPTAUUSDOZ.IDC,881001.WI" # 沪金连一、沪银连一、沪铜连一、伦敦金现、万得全A
# FUTURE_LIST = "J01.DCE,JM01.DCE" # 焦炭连一、焦煤连一
# FUTURE_LIST = "SPGSBRTR.SPI" # 布伦特原油
# FUTURE_LIST = "RB01.SHF,I01.DCE" # 螺纹钢连一、铁矿石连一
# FUTURE_LIST = "C01.DCE,M01.DCE,JD01.DCE" # 玉米连一、豆粕连一、鸡蛋连一
OUTPUT_FILE = "%s.csv"%(NAME)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", help="look back days", default=1, type=int)
    parser.add_argument("--s", help="start date", default="2015-01-01", type=str)
    args = parser.parse_args()
    return args

def calculate_beta(stock_list, future_list, start_date="1990-01-01", k=1):
    ret_dic = {}
    for stock in stock_list:
        ret_dic[stock] = {}

        stock_file = "%s/%s.csv"%(STOCKS_DIR, stock)
        if not os.path.exists(stock_file):
            df = utils.data_from_wind(stock, start_date=start_date)
            df.to_csv(stock_file, index=False)

        for future in future_list:
            future_file = "%s/%s.csv"%(FUTURE_DIR, future)
            if not os.path.exists(future_file):
                df = utils.data_from_wind(future, start_date=start_date)
                df.to_csv(future_file, index=False)

            stock_df = pd.read_csv(stock_file)
            future_df = pd.read_csv(future_file)
            stock_df.index = stock_df["date"].map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))
            future_df.index = future_df["date"].map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))

            stock_df = stock_df["close"].dropna()
            future_df = future_df["close"].dropna()

            stock_df = stock_df[stock_df.index >= future_df.index[0]]
            future_df = future_df[future_df.index >= stock_df.index[0]]

            start_time = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            stock_df = stock_df[stock_df.index >= start_time]
            future_df = future_df[future_df.index >= start_time]

            cov = np.cov(future_df.pct_change(k).dropna().values, stock_df.pct_change(k).dropna().values)
            beta = cov[1, 0] / cov[0, 0]

            print stock, future, beta
            ret_dic[stock][future] = beta

    return ret_dic

def main():
    args = get_args()
    df = pd.read_csv(COMPONENT_FILE.decode('utf-8'))
    stock_list = df["symbol"].tolist()
    future_list = FUTURE_LIST.split(',')
    beta_dict = calculate_beta(stock_list, future_list, start_date=args.s, k=args.k)
    for future in future_list:
        df[future] = 0
        for idx, stock in enumerate(df["symbol"]):
            df.loc[idx, future] = beta_dict[stock][future]
    df.to_csv(OUTPUT_FILE.decode('utf-8'), index=False)

if __name__ == "__main__":
    main()
