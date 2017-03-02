import pandas as pd
import datetime

def wind2df(raw_data):
    dic = {}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[str(field.lower())] = data
    return pd.DataFrame(dic, index=raw_data.Times)

def time2start_date(t):
    if t.find("-") != -1:
        return datetime.datetime.strptime(t, "%Y-%m-%d")
    else:
        return datetime.datetime.strptime(t, "%Y%m%d")
