# encoding: utf-8
# 下载财务数据并保存到文件

from WindPy import w
import pandas as pd
import datetime
import sys

w.start()
factors = ["mkt_cap_ard", # 总市值
           "pe_ttm", # 市盈率
           "pcf_ocf_ttm", # 市现率
           "dividendyield2", # 股息率
           "profit_ttm", # 净利润
           "or_ttm", # 营业收入
           "ps_ttm" # 市销率
          ]

def download(symbol, start_date="2005-01-01", end_date="2016-12-31"):
    current_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    dic = {}
    dates = []
    while current_date <= end_date:
        print current_date.strftime("%Y%m%d")
        raw_data = w.wss(symbol, factors, "tradeDate=%s"%(current_date.strftime("%Y%m%d")))
        for data, field in zip(raw_data.Data, raw_data.Fields):
            if not dic.has_key(str(field.lower())):
                dic[str(field.lower())] = data
            else:
                dic[str(field.lower())].append(data[0])
        dates.append(current_date)
        current_date = current_date + datetime.timedelta(1)

    df = pd.DataFrame(dic)
    df["date"] = dates
    df.to_csv("../data/%s.csv"%(symbol), index=False)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        download(sys.argv[1])
