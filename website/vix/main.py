# encoding: utf-8
import numpy as np
import pandas as pd
import datetime
import os
import sys

from bokeh.io import curdoc
from bokeh.charts import Bar, HeatMap
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from bokeh.models.widgets import Slider, TextInput, TableColumn, DataTable, Select, Button
from bokeh.plotting import figure

import vix.const as const
import vix.data as data
import vix.volatility as volatility
import vix.correlation as correlation

source_vol = ColumnDataSource(data=dict(date=[], vol=[]))
source_cor = ColumnDataSource(data=dict(date=[], cor=[]))
source_table = ColumnDataSource(data=dict())

def update_data():
    asset = const.REV_NAMES[asset_select.value]
    df = volatility.get_dataframe(asset)
    source_vol.data = source_vol.from_df(df)
    plot_vol.title.text = asset_select.value

def update_correlation():
    asset1 = const.REV_NAMES[asset_select.value]
    asset2 = const.REV_NAMES[asset_select2.value]
    df = correlation.get_dataframe(asset1, asset2)
    source_cor.data = source_cor.from_df(df)
    plot_cor.title.text = asset_select.value + " v.s. " + asset_select2.value

def calculate_mean():
    df = pd.read_excel("%s/correlation.xlsx"%(const.DATA_DIR))
    df = df.fillna('')
    source_table.data = source_table.from_df(df)
    # plot_blank.title.text = "Mean Correlation of All: %.2f"%(val)

def update_all():
    update_data()
    update_correlation()
    calculate_mean()

def download_data():
    plot_vol.title.text = "Downloading..."
    data.download_all()
    correlation.all_mean()
    update_all()
    plot_vol.title.text = asset_select.value

asset_selections = const.NAMES.values()
asset_select = Select(value='China ETF Volatility Index', title='Choose VIX Index', width=300, options=asset_selections)
asset_select.on_change('value', lambda attr, old, new: update_all())
asset_select2 = Select(value='Emerging Markets ETF Volatility Index', title='Choose another VIX Index', width=300, options=asset_selections)
asset_select2.on_change('value', lambda attr, old, new: update_correlation())
update_button = Button(label=u'Update Data', width=300, button_type="success")
update_button.on_click(download_data)

tools = "pan,wheel_zoom,box_select,reset"
plot_vol = figure(plot_height=400, plot_width=1000, tools=tools, title='China ETF Volatility Index', x_axis_type='datetime')
plot_vol.line('date', 'vol', source=source_vol, line_width=3, line_alpha=0.6)
plot_vol.title.text_font_size = "15pt"
plot_vol.yaxis.minor_tick_line_color = None
plot_vol.title.text_font = "Microsoft YaHei"

plot_cor = figure(plot_height=400, plot_width=1000, tools=tools,
                  title='China ETF Volatility Index v.s. Emerging Markets ETF Volatility Index', x_axis_type='datetime')
plot_cor.line('date', 'cor', source=source_cor, line_width=3, line_alpha=0.6)
plot_cor.title.text_font_size = "15pt"
plot_cor.yaxis.minor_tick_line_color = None
plot_cor.title.text_font = "Microsoft YaHei"

columns = [TableColumn(field=x, title=x) for x in const.NAMES.keys()]
data_table = DataTable(source=source_table, columns=columns, width=900)

plot_blank = figure(plot_height=50, plot_width=1000, tools=[])
plot_blank.title.text_font_size = "15pt"
plot_blank.title.text_font = "Microsoft YaHei"

inputs = widgetbox(update_button, asset_select, asset_select2)

update_all()

curdoc().add_root(column(inputs, plot_vol, plot_cor, data_table, plot_blank))
curdoc().title = u"VIX Summary"
