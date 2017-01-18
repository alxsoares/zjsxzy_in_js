import pandas as pd
from datetime import datetime
from WindPy import w

w.start()

def Wind2dataframe(raw_data):
    dic = {}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[str.lower(str(field))] = data
    df = pd.DataFrame(dic, index=raw_data.Times)
    return df

def get_contract_data(contract, beginTime="1990-01-01", endTime=datetime.now().strftime("%Y-%m-%d")):
    raw = w.wsd(contract, "close", beginTime=beginTime, endTime=endTime)
    df = Wind2dataframe(raw)
    df.columns = [contract]
    return df

def get_money_fund(beginTime="1990-01-01", endTime=datetime.now().strftime("%Y-%m-%d")):
    security = "H11025.CSI"
    raw = w.wsd(security, "close", beginTime=beginTime, endTime=endTime)
    df = Wind2dataframe(raw)
    df.columns = [security]
    return df
