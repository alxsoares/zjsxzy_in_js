import os
from WindPy import w
import pandas as pd

def fetch_from_wind(csv_dir, symbols, start_date, end_date):
    cols = ["open", "high", "low", "close", "amt"]
    for s in symbols:
        filename = "%s/%s.csv"%(csv_dir, s)
        print filename
        if os.path.exists(filename):
            continue
        raw_data = w.wsd(s, cols, beginTime=start_date, endTime=end_date)
        dic = {}
        for data, field in zip(raw_data.Data, raw_data.Fields):
            if str.lower(str(field)) == "amt":
                field = "volume"
            dic[str.lower(str(field))] = data
        df = pd.DataFrame(dic)
        df["date"] = pd.to_datetime(raw_data.Times)
        df["date"] = df["date"].map(lambda x: x.strftime('%Y-%m-%d'))
        df = df[["date", "open", "high", "low", "close", "volume"]]
        df.dropna(subset=['close'], inplace=True)
        assert(df.shape[0] != 0)
        df.to_csv(filename, index=False)
