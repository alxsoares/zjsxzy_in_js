# encoding: utf-8

import numpy as np
import pandas as pd
import datetime
import os
import sys
from os.path import dirname, join

import word.word_heat_level as word_heat_level
import word.const as const

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource, CustomJS, NumberFormatter
from bokeh.models.widgets import Slider, TextInput, TableColumn, DataTable, Select, Button
from bokeh.plotting import figure

DATA_DIR = "C:/Users/jgtzsx01/Documents/workspace/data/asset-class"

asset_files = [f for f in os.listdir(const.ASSET_DIR) if f.endswith('.csv')]
assets = ['word'] + [a[:-4] for a in asset_files if not a.startswith('H11025')]

source = ColumnDataSource(data=dict(date=[], ts=[]))
source_absolute = ColumnDataSource(data=dict(date=[], ts=[]))
source_weighted = ColumnDataSource(data=dict(date=[], ts=[]))
source_table = ColumnDataSource(data=dict())
source_download = ColumnDataSource(data=dict())
source_absolute_corr = ColumnDataSource(data=dict())
source_corr = ColumnDataSource(data=dict(date=[], corr=[]))
source_per = ColumnDataSource(data=dict())

tools = "pan,wheel_zoom,box_select,reset"
plot = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_absolute = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_weighted = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_corr = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')

plot.line('date', 'ts', source=source, line_width=3, line_alpha=0.6)
plot_absolute.line('date', 'ts', source=source_absolute, line_width=3, line_alpha=0.6)
plot_weighted.line('date', 'ts', source=source_weighted, line_width=3, line_alpha=0.6)
plot_corr.line('date', 'corr', source=source_corr, line_width=3, line_alpha=0.6)

columns = [
    TableColumn(field="word", title="word"),
    TableColumn(field="distance", title="distance")
]
per_columns = [
    TableColumn(field='word', title=u'词'),
    TableColumn(field='percentile', title=u'历史分位', formatter=NumberFormatter(format='0.00%'))
]
data_table = DataTable(source=source_table, columns=columns, width=400, height=300)
per_table = DataTable(source=source_per, columns=per_columns, width=400, height=300)

def update_title():
    plot_absolute.title.text = text.value + u"（绝对）= 周词频"
    plot.title.text = text.value + u"（相对）= 周词频 / 周所有词总词频"
    plot_weighted.title.text = text.value + u"（加权）= 周词频 * 词距离 / 周所有词总词频"

def update_data():
    word = text.value
    threshold = float(slider.value)
    start_date = datetime.datetime(int(year_select.value), 1, 1)

    fname = os.path.join(DATA_DIR, "%s_%.1f.csv"%(word, threshold))
    try:
        if not os.path.exists(fname):
            print("calculating...")
            plot.title.text = "calculating..."
            plot_absolute.title.text = "calculating..."
            plot_weighted.title.text = "calculating..."
            word_heat_level.get_word_heat(word, threshold=threshold)
    except KeyError:
        plot.title.text = u"没有该关键词"
        plot_absolute.title.text = u"没有该关键词"
        plot_weighted.title.text = u"没有该关键词"
        source_table.data = {}
        return

    update_title()

    dataframe = pd.read_csv(fname)
    # dataframe.to_excel("./%s.xlsx"%(text.value), index=False)
    # 可下载数据
    source_download.data = source_download.from_df(dataframe)

    dataframe["date"] = pd.to_datetime(dataframe["date"], format="%Y-%m-%d")
    dataframe = dataframe.set_index('date')
    dataframe = dataframe[dataframe.index >= start_date]
    dataframe = dataframe[dataframe.index <= (datetime.datetime.today() - datetime.timedelta(1))]

    # 加权值曲线
    df = pd.DataFrame({'ts': dataframe["weighted"]})
    source_weighted.data = source_weighted.from_df(df)

    # 相对值曲线
    source.data = source.from_df(pd.DataFrame({'ts': dataframe["relative"]}))

    # 绝对值曲线
    source_absolute.data = source_absolute.from_df(pd.DataFrame({'ts': dataframe['absolute']}))

    # 词表格
    data = pd.read_csv("%s/%s_%s_words.csv"%(DATA_DIR, word, threshold))
    source_table.data = {'word': data['word'], 'distance': data['distance']}

def update_correlation():
    absolute_df = pd.read_excel('%s/absolute_corr.xlsx'%(const.WORD_HEAT_DIR), index_col=None)
    for asset in assets:
        print asset
    absolute_df = absolute_df[assets]
    source_absolute_corr.data = source_absolute_corr.from_df(absolute_df)

def update_percentile():
    df = pd.read_excel('%s/percentile.xlsx'%(const.WORD_HEAT_DIR), index_col=None)
    source_per.data = source_per.from_df(df)

def update_corr():
    asset = asset_text.value
    word = word_text.value
    wfname = '%s/%s_0.5.csv'%(const.WORD_DIR, word)
    afname = '%s/%s.csv'%(const.ASSET_DIR, asset)
    if os.path.exists(wfname) and os.path.exists(afname):
        wdf = pd.read_csv(wfname)
        adf = pd.read_csv(afname)
        wdf.index = pd.to_datetime(wdf['date'], format='%Y-%m-%d')
        adf.index = pd.to_datetime(adf['date'], format='%Y-%m-%d')
        corr = word_heat_level.get_correlation(wdf['relative'], adf['close'])
        source_corr.data = {'date': corr.index, 'corr': corr.values}
        plot_corr.title.text = word + u'词频与' + asset + u'价格相关性'
    else:
        plot_corr.title.text = u'关键词或资产不存在'

years_selections = [str(year) for year in range(2016, 2018)]
year_select = Select(value="2016", title="开始年份", width=200, options=years_selections)
year_select.on_change("value", lambda attr, old, new: update_data())
slider = TextInput(title="阈值", value="0.5")
# slider = Slider(title="阈值", start=0.0, end=1.0, value=0.3, step=0.1)
slider.on_change('value', lambda attr, old, new: update_data())
text = TextInput(title="关键词（例如：MPA、房地产、通胀）", value=u'楼市')
text.on_change('value', lambda attr, old, new: update_data())
button = Button(label=u"下载数据", button_type="success", width=300)
button.callback = CustomJS(args=dict(source=source_download),
                           code=open(join(dirname(__file__), "download.js")).read())

absolute_corr_columns = [TableColumn(field=x, title=x) for x in assets]
absolute_corr_data_table = DataTable(source=source_absolute_corr, columns=absolute_corr_columns, width=1000)
asset_text = TextInput(title=u'资产', value='AU9999.SGE')
asset_text.on_change('value', lambda attr, old, new: update_corr())
word_text = TextInput(title=u'关键词', value=u'加息')
word_text.on_change('value', lambda attr, old, new: update_corr())

update_data()
update_correlation()
update_corr()
update_percentile()

# Set up layouts and add to document
inputs = widgetbox(text, slider, year_select, button)
table = widgetbox(data_table)
text_box = row(asset_text, word_text)

curdoc().add_root(row(inputs, table, plot_absolute, plot, plot_weighted, per_table, absolute_corr_data_table,
                      text_box, plot_corr, width=800))
curdoc().title = u"关键词历史热度"
