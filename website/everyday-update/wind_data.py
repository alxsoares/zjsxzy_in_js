# encoding: utf-8

from WindPy import w
import datetime
import pandas as pd
import const

w.start()

def download_data(symbol,
            start_date="2002-01-01",
            end_date=datetime.datetime.today().strftime("%Y-%m-%d")):
    raw_data = w.wsd(symbol, "close", beginTime=start_date, endTime=end_date)
    dic = {'date': raw_data.Times}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[str(field.lower())] = data
    df = pd.DataFrame(dic)
    df['date'] = df['date'].map(lambda x: x.strftime("%Y-%m-%d"))
    fname = "%s/%s.csv"%(const.DATA_DIR, symbol)
    df.to_csv(fname, index=False)

def download_all(symbols,
                start_date="2002-01-01",
                end_date=datetime.datetime.today().strftime("%Y-%m-%d")):
    for symbol in symbols:
        download_data(symbol, start_date=start_date, end_date=end_date)

if __name__ == "__main__":
    download_data("HSI.HI")
