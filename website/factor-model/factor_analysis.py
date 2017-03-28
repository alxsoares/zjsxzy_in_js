# encoding: utf-8
import pandas as pd
import numpy as np
import sys

sys.path.append("C:/Users/jgtzsx01/Documents/workspace/zjsxzy_in_js/factor-investing/src/")

import const

def get_data(factor_name, metric="Normal_IC"):
    fname = "%s/%s_%s.xlsx"%(const.DATA_DIR, factor_name, metric)
    df = pd.read_excel(fname, index_col=0)
    df.index = pd.to_datetime(df.index, format="%Y-%m-%d")
    return df

def get_ic_dataframe(factor_name, metric="Normal_IC", window=20):
    df = get_data(factor_name, metric=metric)
    data_df = pd.DataFrame({"date": df.index, "ic": df[str(window)].values})
    return data_df

def get_cone_dataframe(factor_name, metric="Normal_IC"):
    df = get_data(factor_name, metric=metric)
    ks = const.ks
    today = df.index[-2]
    data_df = pd.DataFrame({"days": ks, 'ic': df.ix[today].values,
                            "max": df.max(axis=0).values, "min": df.min(axis=0).values,
                            "median": df.median(axis=0).values,
                            "percent_75": df.quantile(0.75, axis=0).values,
                            "percent_25": df.quantile(0.25, axis=0).values})
    return data_df
