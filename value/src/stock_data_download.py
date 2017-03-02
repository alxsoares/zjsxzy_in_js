# encoding: utf-8
# 下载所有股票数据

from WindPy import w
import datetime

import utils

def download():
    w.start()
    start_date = "1990-01-01"
    end_date = "2016-12-31"
    csv_dir = "D:/Data/stocks"
    index = "881001.WI"
    codes = w.wset("IndexConstituent","date=%s;windcode=%s;field=wind_code"%(end_date, index))
    codes = codes.Data[0]
    utils.fetch_from_wind(csv_dir, codes, start_date, end_date)

if __name__ == "__main__":
    # fetch_from_wind("D:/Data/stocks", ["000001.SZ", "000002.SZ"], "1990-01-01", "2016-12-31")
    download()
