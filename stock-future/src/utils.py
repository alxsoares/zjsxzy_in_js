from WindPy import w
import pandas as pd

def data_from_wind(symbol, start_date="1990-01-01", end_date="2017-02-06"):
    w.start()
    cols = ["open", "high", "low", "close", "amt"]
    raw_data = w.wsd(symbol, cols, beginTime=start_date, endTime=end_date)
    dic = {}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[str.lower(str(field))] = data
    df = pd.DataFrame(dic)
    df["date"] = pd.to_datetime(raw_data.Times)
    df["date"] = df["date"].map(lambda x: x.strftime('%Y-%m-%d'))
    df.dropna(subset=['close'], inplace=True)
    assert(df.shape[0] != 0)
    return df
