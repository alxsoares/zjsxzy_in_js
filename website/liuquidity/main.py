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
from bokeh.models.widgets import Slider, TextInput, TableColumn, DataTable, Select, Button, PreText
from bokeh.plotting import figure

source = ColumnDataSource(data=dict(date=[], stock=[], bond=[]))

fname = "C:/Users/jgtzsx01/Documents/sheet/liquidity.xlsx"
df = pd.read_excel(fname)
df['date'] = pd.to_datetime(df['date'], format="%Y/%m/%d")

source.data = source.from_df(df)

tools = "pan,wheel_zoom,box_select,reset"
plot1 = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot1.vbar(x='date', top='stock', bottom=0, width=1, source=source)
plot1.title.text_font_size = "15pt"
plot1.yaxis.minor_tick_line_color = None
plot1.title.text_font = "Microsoft YaHei"
plot1.title.text = u"股票流动性风险"
plot2 = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot2.vbar(x='date', top='bond', bottom=0, width=1, source=source)
plot2.title.text_font_size = "15pt"
plot2.yaxis.minor_tick_line_color = None
plot2.title.text_font = "Microsoft YaHei"
plot2.title.text = u"债券流动性风险"

curdoc().add_root(column(plot1, plot2))
curdoc().title = u"流动性风险"
