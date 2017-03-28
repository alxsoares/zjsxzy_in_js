# encoding: utf-8

import numpy as np
import pandas as pd
import datetime
import os
import sys

import utils
import factor_analysis
sys.path.append("C:/Users/jgtzsx01/Documents/workspace/zjsxzy_in_js/factor-investing/src/")
import factors
import const

from bokeh.io import curdoc
from bokeh.charts import Bar
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from bokeh.models.widgets import Slider, TextInput, TableColumn, DataTable, Select, Button, PreText
from bokeh.plotting import figure

fname = const.STOCK_FILE
groups = 5
source_value = ColumnDataSource(data=dict(date=[], value5=[], value4=[], value3=[], value2=[], value1=[]))
source_return = ColumnDataSource(data=dict(date=[], returns=[]))
source_group = ColumnDataSource(data=dict(left=[], right=[], top=[], bottom=[], text=[], text_y=[]))
source_ic = ColumnDataSource(data=dict(date=[], ic=[]))
source_cone = ColumnDataSource(data=dict(days=[], ic=[], max=[], min=[], median=[], percent_75=[], percent_25=[]))

factors_list = ["5-day return",
                "120-day return",
                "30-day average return",
                "pe_percent",
                "30-day volatility"]
ks = [str(k) for k in const.ks]
metrics = ["Normal_IC", "Mutual Information"]

def recalculate():
    plot_return.title.text = u"计算中..."
    plot_value.title.text = u"计算中..."
    plot_group.title.text = u"计算中..."

    weights = [float(five_day_return_text.value),
               float(hundred_twenty_day_return_text.value),
               float(thirty_day_average_return_text.value),
               float(pe_text.value),
               float(thirty_day_volatility.value)]

    # factors_list = [f for (f, w) in zip(factors_list, weights) if w != 0]
    # weights = [w for w in weights if w != 0]
    # print(factors_list)
    # print(weights)

    df = factors.read_asset_set(fname)
    pnl = factors.get_asset_factor_data(df, factors_list, frequency='m')
    # pnl = factors.get_predict_return(pnl, factors_list,
                                    #  train_date=train_date_text.value,
                                    #  test_date=test_date_text.value)
    pnl = factors.get_score_return(pnl, factors_list, weights)
    group_df = factors.get_group_return(pnl)
    group_df.to_excel("groups.xlsx")

    plot_return.title.text = u"第五组每期收益率"
    plot_value.title.text = u"第五组净值"
    plot_group.title.text = u"每组每期平均收益率"
    update_data()

def update_factor_data():
    factor_name = factor_select.value
    window = int(window_select.value)

    data_df = factor_analysis.get_ic_dataframe(factor_name, metric=metrics_select.value, window=window)
    source_ic.data = source_ic.from_df(data_df)

    data_df = factor_analysis.get_cone_dataframe(factor_name, metric=metrics_select.value)
    source_cone.data = source_cone.from_df(data_df)

def update_data():
    group_df = pd.read_excel("groups.xlsx", index_col=0)
    group_df = group_df[group_df.index >= test_date_text.value]

    source_return.data = {"date": group_df.index, "returns": group_df[5].values}

    acc_return = (1 + group_df[5]).cumprod()
    data = {"date": acc_return.index, "value5": acc_return.values}
    for i in range(1, groups):
        data["value%d"%(i)] = (1 + group_df[i]).cumprod().values
    source_value.data = data

    mean_return = group_df.mean().values
    mean_return = (1 + mean_return)**12 - 1
    df = pd.DataFrame({"top": mean_return})
    df.loc[:, "bottom"] = [0] * groups
    df.loc[:, "left"] = range(groups)
    df.loc[:, "right"] = [x+0.5 for x in df["left"]]
    df.loc[:, "text"] = [u"第%d组"%(x) for x in range(1, groups+1)]
    df.loc[:, "text_y"] = [-0.3] * groups
    source_group.data = source_group.from_df(df)

tools = "pan,wheel_zoom,box_select,reset"
plot_normal_ic = figure(plot_height=400, plot_width=1000, tools=tools, y_range=[-1., 1.], x_axis_type='datetime')
plot_normal_ic.vbar(x='date', top='ic', bottom=0, width=1, source=source_ic)
plot_normal_ic.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_normal_ic.title.text_font_size = "15pt"
plot_normal_ic.yaxis.minor_tick_line_color = None
plot_normal_ic.title.text_font = "Microsoft YaHei"
plot_normal_ic.title.text = u"因子IC"

plot_cone = figure(plot_height=400, plot_width=1000, tools=tools)
plot_cone.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_cone.title.text_font_size = "15pt"
plot_cone.yaxis.minor_tick_line_color = None
plot_cone.title.text_font = "Microsoft YaHei"
plot_cone.line('days', 'max', source=source_cone, line_width=2, color='#002EB8', legend='Max')
plot_cone.line('days', 'percent_75', source=source_cone, line_width=2, color='#003DF5', legend='3/4')
plot_cone.line('days', 'median', source=source_cone, line_width=2, color='#33CCFF', legend='Median')
plot_cone.line('days', 'percent_25', source=source_cone, line_width=2, color='#33FFCC', legend='1/4')
plot_cone.line('days', 'min', source=source_cone, line_width=2, color='#33FF66', legend='Min')
plot_cone.line('days', 'ic', source=source_cone, line_width=5, color='red', legend='Now')
plot_cone.title.text = u"因子IC锥"

plot_group = figure(plot_height=400, plot_width=1000, tools=tools, x_range=[-0.5, groups], y_range=[-0.3, 0.6], title="每组每期平均收益率")
plot_group.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_group.quad(left='left', right='right', bottom='bottom', top='top', source=source_group)
plot_group.text(x='left', y='text_y', text='text', source=source_group, text_font_size='12pt', angle=0.5)
plot_group.xaxis.visible = False
plot_group.title.text_font_size = "15pt"
plot_group.yaxis.minor_tick_line_color = None

plot_value = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type="datetime")
plot_value.line(x='date', y='value5', source=source_value, line_width=3, line_alpha=0.6, color="blue", legend=u"第五组")
plot_value.line(x='date', y='value4', source=source_value, line_width=3, line_alpha=0.6, color="#003DF5", legend=u"第四组")
plot_value.line(x='date', y='value3', source=source_value, line_width=3, line_alpha=0.6, color="#33CCFF", legend=u"第三组")
plot_value.line(x='date', y='value2', source=source_value, line_width=3, line_alpha=0.6, color="#33FFCC", legend=u"第二组")
plot_value.line(x='date', y='value1', source=source_value, line_width=3, line_alpha=0.6, color="#33FF66", legend=u"第一组")
plot_value.title.text_font_size = "15pt"
plot_value.yaxis.minor_tick_line_color = None
plot_value.title.text_font = "Microsoft YaHei"
plot_value.title.text = u"五组净值"

plot_return = figure(plot_height=400, plot_width=1000, tools=tools, y_range=[-0.5, 0.5], x_axis_type='datetime')
plot_return.vbar(x='date', top='returns', bottom=0, width=1, source=source_return)
plot_return.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_return.title.text_font_size = "15pt"
plot_return.yaxis.minor_tick_line_color = None
plot_return.title.text_font = "Microsoft YaHei"
plot_return.title.text = u"第五组每期收益率"

train_date_text = TextInput(value="2010-01-01", title=u"训练开始日期", width=200)
test_date_text = TextInput(value="2014-01-01", title=u"测试开始日期", width=200)

momentum_factors = PreText(text=u"动量因子：", width=200, height=20)
five_day_return_text = TextInput(value="1", title=u"5日收益率", width=200)
hundred_twenty_day_return_text = TextInput(value="1", title=u"120日收益率", width=200)
thirty_day_average_return_text = TextInput(value="1", title=u"30日平均收益率", width=200)

value_factors = PreText(text=u"价值因子：", width=200, height=20)
pe_text = TextInput(value="2", title=u"PE", width=200)

defensive_factors = PreText(text=u"防御因子：", width=200, height=20)
thirty_day_volatility = TextInput(value="2", title=u"30日波动率", width=200)

update_button = Button(label=u"重新回测", width=300, button_type="success")
update_button.on_click(recalculate)

factor_select = Select(value="pe_percent", title=u"选择因子", width=300, options=factors_list)
factor_select.on_change('value', lambda attr, old, new: update_factor_data())
window_select = Select(value='20', title=u'选择窗口', width=300, options=ks)
window_select.on_change('value', lambda attr, old, new: update_factor_data())
metrics_select = Select(value="Normal_IC", title=u"因子衡量标准", width=300, options=metrics)

recalculate()
update_data()
update_factor_data()

time_input = row(train_date_text, test_date_text)
momentum_factor_input = row(five_day_return_text, hundred_twenty_day_return_text, thirty_day_average_return_text)
value_factor_input = row(pe_text)
defensive_factor_input = row(thirty_day_volatility)
factor_input = row(factor_select, window_select, metrics_select)
inputs = column(time_input,
                momentum_factors, momentum_factor_input,
                value_factors, value_factor_input,
                defensive_factors, defensive_factor_input,
                factor_input)

curdoc().add_root(column(inputs, update_button, plot_normal_ic, plot_cone, plot_group, plot_value, plot_return))
curdoc().title = u"因子模型"
