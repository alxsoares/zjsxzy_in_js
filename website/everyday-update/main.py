# encoding: utf-8

import numpy as np
import pandas as pd
import datetime
import os
import sys

from bokeh.io import curdoc
from bokeh.charts import Bar
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from bokeh.models.widgets import Slider, TextInput, TableColumn, DataTable, Select, Button
from bokeh.plotting import figure
from bokeh.palettes import Spectral9

import wind_data
import utils
import correlation
import volatility
import price
import const

ASSETS_NAME = {"881001.WI": u"万得全A指数",
                "HSI.HI": u"恒生指数",
                "SPX.GI": u"标普500",
                "SX5P.GI": u"欧洲50",
                "065.CS": u"中债新综合财富指数",
                "SPGSCITR.SPI": u"商品总指数",
                "USDX.FX": u"美元指数",
                "USDCNY.FX": u"美元兑人民币",
                "AU(T+D).SGE": u"SGE黄金T+D",
                "B.IPE": u"WTI原油",
                "CA.LME": u"LME铜",
                "VIX.GI": u"隐含波动率指数"}
COLORS = Spectral9
COLORS += ["#053061", "#2166ac", "#4393c3"] # "#92c5de", "#d1e5f0", "#f7f7f7", "#fddbc7", "#f4a582", "#d6604d", "#b2182b"]
ASSETS_NAME = {key: value for key, value in ASSETS_NAME.iteritems()}
ASSETS_REV_NAME = {value: key for key, value in ASSETS_NAME.iteritems()}
ASSETS_COLOR = {asset: COLORS[i] for i, asset in enumerate(ASSETS_NAME.values())}
asset_selections = ASSETS_NAME.values()

source_price = ColumnDataSource(data=dict(date=[], close=[]))
source_sharpe = ColumnDataSource(data=dict(left=[], right=[], top=[], bottom=[], text=[], sharpe=[], color=[], text_pos=[]))
source_vol = ColumnDataSource(data=dict(days=[], vol=[], max=[], min=[], median=[], percent_75=[], percent_25=[]))
source_cor = ColumnDataSource(data=dict(days=[], cor=[], max=[], min=[], median=[], percent_75=[], percent_25=[]))

def update_title():
    plot_price.title.text = asset_select.value

def time2start_date(t):
    if t.find("-") != -1:
        return datetime.datetime.strptime(t, "%Y-%m-%d")
    else:
        return datetime.datetime.strptime(t, "%Y%m%d")

def update_data():
    start_date = time2start_date(time_text.value)
    end_date = time2start_date(time_end_text.value)
    symbol = ASSETS_REV_NAME[asset_select.value]

    dataframe = price.get_dataframe(symbol, start_date, end_date)
    print dataframe.head()
    update_title()
    source_price.data = {'close': dataframe['close'].values, 'date': dataframe.index}
    plot_price.line('date', 'close', source=source_price, line_width=5, line_alpha=0.6, color=ASSETS_COLOR[asset_select.value])

    update_volatility()
    plot_vol.title.text = asset_select.value + u"波动率锥"

def update_statistics():
    plot_sharpe.title.text = u"计算中..."
    start_date = time2start_date(time_text.value)
    end_date = time2start_date(time_end_text.value)

    num_asset = len(asset_selections)
    bottom = [0 for i in range(num_asset)]
    top = [] # sharpe ratio
    text = asset_selections
    color = COLORS

    for asset in asset_selections:
        symbol = ASSETS_REV_NAME[asset]
        fname = "%s/%s.csv"%(const.DATA_DIR, symbol)
        if not os.path.exists(fname):
            wind_data.download_data(symbol)
        dataframe = pd.read_csv(fname)
        dataframe['date'] = pd.to_datetime(dataframe['date'], format="%Y-%m-%d")
        dataframe = dataframe.set_index('date')
        dataframe['return'] = dataframe['close'].pct_change()
        dataframe = dataframe[(dataframe.index >= start_date) & (dataframe.index <= end_date)]
        dataframe.dropna(inplace=True)
        sharpe = utils.get_sharpe_ratio(dataframe['return'])
        top.append(sharpe)

    df = pd.DataFrame({"bottom": bottom, "top": top, "text": text,
                        "sharpe": ["%.2f"%(x) for x in top], 'color': color})
    df.sort_values('top', inplace=True, ascending=False)
    df['left'] = range(num_asset)
    df['right'] = [x+0.5 for x in df['left']]
    df['text_pos'] = [x+0.15 for x in df['left']]
    plot_sharpe.title.text = u"资产夏普率"
    source_sharpe.data = source_sharpe.from_df(df)

def update_volatility():
    start_date = time2start_date(time_text.value)
    end_date = time2start_date(time_end_text.value)
    symbol = ASSETS_REV_NAME[asset_select.value]

    data_df = volatility.get_dataframe(symbol, start_date, end_date)
    source_vol.data = source_vol.from_df(data_df)
    plot_vol.line(x='days', y='vol', source=source_vol, line_width=5, line_alpha=0.6, color=ASSETS_COLOR[asset_select.value])

def update_correlation():
    start_date = time2start_date(time_text.value)
    end_date = time2start_date(time_end_text.value)
    symbol1 = asset_text_1.value
    symbol2 = asset_text_2.value

    data_df = correlation.get_dataframe(symbol1, symbol2, start_date, end_date)
    plot_correlation.title.text = asset_text_1.value + u"与" + asset_text_2.value + u"相关性锥"
    source_cor.data = source_cor.from_df(data_df)

def update_all():
    update_data()
    update_statistics()
    update_correlation()

asset_select = Select(value=u"万得全A指数", title="资产", width=300, options=asset_selections)
asset_select.on_change('value', lambda attr, old, new: update_data())
time_text = TextInput(value="2002-01-01", title="开始时间（例如：20050101或2005-01-01）", width=300)
time_text.on_change('value', lambda attr, old, new: update_all())
today = datetime.datetime.today()
time_end_text = TextInput(value=today.strftime("%Y-%m-%d"), title="终止时间", width=300)
time_end_text.on_change('value', lambda attr, old, new: update_all())
asset_text_1 = TextInput(value="881001.WI", title=u"资产一（万得代码）", width=300)
asset_text_2 = TextInput(value="HSI.HI", title=u"资产二（万得代码）", width=300)

tools = "pan,wheel_zoom,box_select,reset"
plot_price = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_price.title.text_font_size = "15pt"
plot_price.yaxis.minor_tick_line_color = None
plot_price.title.text_font = "Microsoft YaHei"

plot_vol = figure(plot_height=400, plot_width=1000, tools=tools)
plot_vol.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_vol.title.text_font_size = "15pt"
plot_vol.yaxis.minor_tick_line_color = None
plot_vol.title.text_font = "Microsoft YaHei"
plot_vol.line('days', 'max', source=source_vol, line_width=2, color='#002EB8', legend='Max')
plot_vol.line('days', 'percent_75', source=source_vol, line_width=2, color='#003DF5', legend='3/4')
plot_vol.line('days', 'median', source=source_vol, line_width=2, color='#33CCFF', legend='Median')
plot_vol.line('days', 'percent_25', source=source_vol, line_width=2, color='#33FFCC', legend='1/4')
plot_vol.line('days', 'min', source=source_vol, line_width=2, color='#33FF66', legend='Min')

plot_sharpe = figure(plot_height=400, plot_width=1000, tools=tools, x_range=[-0.5, len(asset_selections)], y_range=[-6, 10], title="资产夏普率")
plot_sharpe.quad(left='left', right='right', bottom='bottom', top='top', source=source_sharpe, color='color')
plot_sharpe.text(x='left', y=-5, text='text', source=source_sharpe, text_font_size='9pt', angle=0.5)
plot_sharpe.text(x='text_pos', y='top', text='sharpe', source=source_sharpe, text_font_size='10pt')
plot_sharpe.xaxis.visible = False
plot_sharpe.yaxis.axis_label = u"Sharpe Ratio"
plot_sharpe.title.text_font_size = "15pt"
plot_sharpe.yaxis.minor_tick_line_color = None

plot_correlation = figure(plot_height=400, plot_width=1000, tools=tools)
plot_correlation.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_correlation.title.text_font_size = "15pt"
plot_correlation.yaxis.minor_tick_line_color = None
plot_correlation.title.text_font = "Microsoft YaHei"
plot_correlation.line('days', 'cor', source=source_cor, line_width=5, color='red', legend='Now')
plot_correlation.line('days', 'max', source=source_cor, line_width=2, color='#002EB8', legend='Max')
plot_correlation.line('days', 'percent_75', source=source_cor, line_width=2, color='#003DF5', legend='3/4')
plot_correlation.line('days', 'median', source=source_cor, line_width=2, color='#33CCFF', legend='Median')
plot_correlation.line('days', 'percent_25', source=source_cor, line_width=2, color='#33FFCC', legend='1/4')
plot_correlation.line('days', 'min', source=source_cor, line_width=2, color='#33FF66', legend='Min')

plot_blank = figure(plot_height=400, plot_width=1000, tools=[])

update_all()

asset_text_1 = TextInput(value="881001.WI", title=u"资产一", width=300)
asset_text_2 = TextInput(value="HSI.HI", title=u"资产二", width=300)
update_button = Button(label=u"计算相关性", width=300, button_type="success")
update_button.on_click(update_correlation)
asset_row = row(asset_text_1, asset_text_2, update_button)

inputs = widgetbox(time_text, time_end_text, asset_select)

curdoc().add_root(column(inputs, plot_sharpe, plot_price, plot_vol, asset_row, plot_correlation, plot_blank))
curdoc().title = u"每日资产总结"
