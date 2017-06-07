import pandas as pd
import numpy as np

def profit_predict(df, k=5):
    df['return'] = df['close'].pct_change(k)
    df['y'] = df['return'].shift(-k)
    return df['y'].corr(df['profit percentage'])
