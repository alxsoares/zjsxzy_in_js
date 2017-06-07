# encoding: utf-8
import pandas as pd

import const

def get_dataframe():
    fname = '%s/price.pkl'%(const.DATA_DIR)
    pnl = pd.read_pickle(fname)
    pnl.ix[:, :, 'year'] = pnl.minor_xs('close').rolling(window=242).mean()
    price = pnl.minor_xs('close') > pnl.minor_xs('year')
    array = price.sum(axis=1) / (~pnl.minor_xs('close').isnull()).sum(axis=1)
    df = pd.DataFrame({'year': array.values}, index=array.index)
    df.index.name = 'date'
    pnl.ix[:, :, 'quarter'] = pnl.minor_xs('close').rolling(window=61).mean()
    price = pnl.minor_xs('close') > pnl.minor_xs('quarter')
    array = price.sum(axis=1) / (~pnl.minor_xs('close').isnull()).sum(axis=1)
    df['quarter'] = array.values
    return df

if __name__ == '__main__':
    df = get_dataframe()
    print df
