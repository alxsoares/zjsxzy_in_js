# encoding: utf-8
import pandas as pd
import numpy as np
import datetime
from WindPy import w
from sklearn.decomposition import PCA

import wind_data
import utils

codes = ['CI0050%02d.WI'%(i) for i in range(1, 30)]
fields = 'close'
INDEX_DIR = 'D:/Data/index'

def download_data(codes,
                  fields,
                  start_date='2012-01-01',
                  end_date='2017-03-30'):
    for code in codes:
        print(code)
        data = w.wsd(code, fields, start_date, end_date)
        df = wind_data.wind2df(data)
        df.to_excel('%s/%s.xlsx'%(INDEX_DIR, code))

def append_data(codes,
                fileds):
    for code in codes:
        print(code)
        fname = '%s/%s.xlsx'%(INDEX_DIR, code)
        old_df = pd.read_excel(fname, index_col=0)
        start_date = old_df.index[-1] + datetime.timedelta(1)
        if datetime.datetime.now().hour < 15:
            end_date = datetime.datetime.today() - datetime.timedelta(1)
        else:
            end_date = datetime.datetime.today()
        if start_date > end_date:
            continue
        else:
            data = w.wsd(code, fields, start_date, end_date)
            df = wind_data.wind2df(data)
            df = old_df.append(df)
            df.to_excel(fname)

def get_panel():
    dic = {}
    for code in codes:
        temp = pd.read_excel('%s/%s.xlsx'%(INDEX_DIR, code), index_col=0)
        dic[code] = temp
    pnl = pd.Panel(dic)
    return pnl

def principal_ratio(df, k):
    pca = PCA()
    pca.fit(df)
    pricipal = pca.explained_variance_ratio_
    return pricipal[:k].sum()

def get_dataframe():
    pnl = get_panel()
    pnl.ix[:, :, 'return'] = pnl.minor_xs('close').pct_change()
    df = pnl.minor_xs('return')

    rolled_df = utils.roll(df, 60)
    ratio = rolled_df.apply(lambda x: principal_ratio(x, 3))

    res = pd.DataFrame({'con60': ratio})
    res.index.name = 'date'

    return res

def main():
    append_data(codes, fields)

if __name__ == '__main__':
    # download_data(codes, fields)
    main()
