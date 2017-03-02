# encoding: utf-8

import numpy as np
import pandas as pd
import datetime
import os
import sys

import utils
import momentum
import value
import beta

from bokeh.io import curdoc
from bokeh.charts import Bar
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from bokeh.models.widgets import Slider, TextInput, TableColumn, DataTable, Select, Button, PreText
from bokeh.plotting import figure

ASSETS_NAME = {"881001.WI": u"万得全A指数",
                "HSI.HI": u"恒生指数",
                "SPX.GI": u"标普500",
                "SX5P.GI": u"欧洲50",
                "065.CS": u"中债新综合财富指数",
                "SPGSCITR.SPI": u"商品总指数",
                "USDX.FX": u"美元指数",
                "USDCNY.FX": u"美元兑人民币",
                "AU(T+D).SGE": u"SGE黄金T+D",
                "T.IPE": u"WTI原油",
                "CA.LME": u"LME铜",
                "VIX.GI": u"隐含波动率指数"}
ASSETS_REV_NAME = {value: key for key, value in ASSETS_NAME.iteritems()}
asset_selections = ASSETS_NAME.values()

source_momentum = ColumnDataSource(data=dict(date=[], price=[], avg_return=[], sharpe=[]))
source_value = ColumnDataSource(data=dict(date=[], pe=[], pb=[]))
source_beta = ColumnDataSource(data=dict(days=[], beta=[], min=[], max=[], median=[], percent_75=[], percent_25=[]))

def update_data():
    asset_code = ASSETS_REV_NAME[asset_select.value]
    look_back = int(look_back_text.value)
    start_date = utils.time2start_date(start_date_text.value)
    end_date = utils.time2start_date(end_date_text.value)
    momentum_df = momentum.get_dataframe(asset_code, look_back, start_date, end_date)
    value_df = value.get_dataframe(asset_code, start_date, end_date)

    plot_momentum.title.text = asset_select.value + u"动量因子"
    plot_value.title.text = asset_select.value + u"价值因子"

    source_momentum.data = source_momentum.from_df(momentum_df)
    source_value.data = source_value.from_df(value_df)

def update_beta():
    stock_code = stock_choose.value
    index_code = index_choose.value
    start_date = utils.time2start_date(start_date_text.value)
    end_data = utils.time2start_date(end_date_text.value)

    plot_beta.title.text = stock_code + u"与" + index_code + u"Beta锥"

    beta_df = beta.get_dataframe(stock_code, index_code, start_date, end_data)
    source_beta.data = source_beta.from_df(beta_df)

asset_select = Select(value=u"万得全A指数", title=u"资产", width=300, options=asset_selections)
asset_select.on_change('value', lambda attr, old, new: update_data())
look_back_text = TextInput(value="30", title=u"回看天数k", width=300)
look_back_text.on_change('value', lambda attr, old, new: update_data())
start_date_text = TextInput(value="2010-01-01", title=u"开始时间", width=300)
start_date_text.on_change('value', lambda attr, old, new: update_data())
today = datetime.datetime.today()
end_date_text = TextInput(value=today.strftime("%Y-%m-%d"), title=u"结束时间", width=300)
end_date_text.on_change('value', lambda attr, old, new: update_data())

tools = "pan,wheel_zoom,box_select,reset"
plot_momentum = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_momentum.line('date', 'price', source=source_momentum, line_width=3, line_alpha=0.6)
plot_momentum.line('date', 'avg_return', source=source_momentum, line_width=3, line_alpha=0.6, color='green', legend=u'过去k日平均收益率')
plot_momentum.line('date', 'sharpe', source=source_momentum, line_width=3, line_alpha=0.6, color='yellow', legend=u"过去k日夏普率")
plot_momentum.title.text_font_size = "15pt"
plot_momentum.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_momentum.yaxis.minor_tick_line_color = None
plot_momentum.title.text_font = "Microsoft YaHei"

plot_value = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_value.line('date', 'pe', source=source_value, line_width=3, line_alpha=0.6, color='green', legend=u"市场平均PE")
plot_value.line('date', 'pb', source=source_value, line_width=3, line_alpha=0.6, color='yellow', legend=u"市场平均PB")
plot_value.title.text_font_size = "15pt"
plot_value.yaxis.minor_tick_line_color = None
plot_value.title.text_font = "Microsoft YaHei"

stock_choose = TextInput(value="000002.SZ", title=u"股票代码", width=300)
stock_choose.on_change('value', lambda attr, old, new: update_beta())
index_choose = TextInput(value="881001.WI", title=u"指数代码", width=300)
index_choose.on_change('value', lambda attr, old, new: update_beta())

plot_beta = figure(plot_height=400, plot_width=1000, tools=tools)
plot_beta.title.text_font_size = "15pt"
plot_beta.yaxis.minor_tick_line_color = None
plot_beta.title.text_font = "Microsoft YaHei"
plot_beta.line('days', 'beta', source=source_beta, line_width=5, color='red', legend='Current Beta')
plot_beta.line('days', 'max', source=source_beta, line_width=2, color='#002EB8', legend='Max')
plot_beta.line('days', 'percent_75', source=source_beta, line_width=2, color='#003DF5', legend='3/4')
plot_beta.line('days', 'median', source=source_beta, line_width=2, color='#33CCFF', legend='Median')
plot_beta.line('days', 'percent_25', source=source_beta, line_width=2, color='#33FFCC', legend='1/4')
plot_beta.line('days', 'min', source=source_beta, line_width=2, color='#33FF66', legend='Min')

update_data()
update_beta()
inputs = widgetbox(start_date_text, end_date_text, look_back_text, asset_select)

curdoc().add_root(column(inputs, plot_momentum, plot_value, row(stock_choose, index_choose), plot_beta))
curdoc().title = "Factor Investing"
