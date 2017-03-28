# encoding: utf-8

import pandas as pd
import calendar

def last_day_of_month(name):
    date = name.split(' ')[0]
    [year, month] = date.split('-')
    year, month = int(year), int(month)
    _, day = calendar.monthrange(year, month)
    date = "%d-%d-%d"%(year, month, day)
    return pd.to_datetime(date, format="%Y-%m-%d")
