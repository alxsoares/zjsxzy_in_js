# encoding: utf-8

from WindPy import w
import datetime
import pandas as pd
import os

import const

ASSETS_NAME = {"881001.WI": u"万得全A指数",
                "HSI.HI": u"恒生指数",
                "SPX.GI": u"标普500",
                "SX5P.GI": u"欧洲50",
                "065.CS": u"中债新综合财富指数",
                "SPGSCITR.SPI": u"商品总指数",
                "USDX.FX": u"美元指数",
                "USDCNY.FX": u"美元兑人民币",
                "AU9999.SGE": u"黄金9999（民生银行）",
                "B.IPE": u"WTI原油",
                "CA.LME": u"LME铜",
                "VIX.GI": u"隐含波动率指数"}

w.start()

def wind2df(raw_data):
    dic = {}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[str(field.lower())] = data
    df = pd.DataFrame(dic, index=raw_data.Times)
    return df

def download_data(symbol,
            start_date="2010-01-01",
            end_date=datetime.datetime.today().strftime("%Y-%m-%d")):
    print start_date, end_date
    raw_data = w.wsd(symbol, "close", beginTime=start_date, endTime=end_date)
    dic = {'date': raw_data.Times}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[str(field.lower())] = data
    df = pd.DataFrame(dic)
    df['date'] = df['date'].map(lambda x: x.strftime("%Y-%m-%d"))
    fname = "%s/%s.csv"%(const.DATA_DIR, symbol)
    df.to_csv(fname, index=False)

def download_all(symbols,
                start_date="2010-01-01",
                end_date=datetime.datetime.today().strftime("%Y-%m-%d")):
    for symbol in symbols:
        print symbol
        download_data(symbol, start_date=start_date, end_date=end_date)

def get_component(symbols,
                  date=datetime.datetime.today().strftime("%Y-%m-%d")):
    data = w.wset("sectorconstituent","date=%s;windcode=%s"%(date, symbols))
    df = wind2df(data)
    df = df[["sec_name", "wind_code"]]
    df.columns = ["name", "code"]
    df.to_excel("%s/%s.xlsx"%(const.INDEX_DIR, symbols), index=False)

def column_append(ticker,
                  fields,
                  start_date='2015-01-01',
                  end_date='2017-03-28'):
    fname = '%s/%s.xlsx'%(const.STOCK_DIR, ticker)
    old_df = pd.read_excel(fname, index_col=0)
    for col in fields.split(','):
        if col in old_df.columns:
            return

    print ticker
    data = w.wsd(ticker, fields, start_date, end_date, "traderType=1")
    df = wind2df(data)
    assert(df.shape[0] == old_df.shape[0])
    df = old_df.join(df)
    df.to_excel(fname)

def get_stock_price_panel():
    files = [f for f in os.listdir(const.STOCK_DIR)]
    dic = {}
    for f in files:
        fname = '%s/%s'%(const.STOCK_DIR, f)
        df = pd.read_excel(fname, index_col=0)
        dic[f[:9]] = df[['close']]
    pnl = pd.Panel(dic)
    pnl.to_pickle('%s/price.pkl'%(const.DATA_DIR))

def main():
    get_stock_price_panel()
    download_all(ASSETS_NAME.keys())

if __name__ == "__main__":
    main()
