import pandas as pd
import numpy as np

import const

def get_dataframe(asset):
    df = pd.read_csv('%s/%s.csv'%(const.DATA_DIR, asset))
    df.columns = [x.rstrip() for x in df.columns]
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
        df.set_index('Date', inplace=True)
    if 'Trade_date' in df.columns:
        df['Trade_date'] = pd.to_datetime(df['Trade_date'], format='%m/%d/%Y')
        df.set_index('Trade_date', inplace=True)
    df.index.name = 'date'
    df = df[df.index >= const.start_date]

    if 'Close' not in df.columns:
        if len(df.columns) == 1:
            df.columns = ['Close']
    df['Close'] = df['Close'].astype(np.float64)
    return pd.DataFrame({'vol': df['Close']}, index=df.index)

if __name__ == '__main__':
    df = get_dataframe('VXO')
