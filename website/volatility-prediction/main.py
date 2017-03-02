# encoding: utf-8

import numpy as np
import pandas as pd
import datetime
import os
import sys

import utils
import volatility

from bokeh.io import curdoc
from bokeh.charts import Bar
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from bokeh.models.widgets import Slider, TextInput, TableColumn, DataTable, Select, Button, PreText
from bokeh.plotting import figure

KEY_WORD = {"881001.WI": u"股票",
            "HSI.HI": u"港股",
            "SPX.GI": u"美股",
            "SX5P.GI": u"欧洲",
            "065.CS": u"债",
            "SPGSCITR.SPI": u"商品",
            "USDX.FX": u"美元",
            "USDCNY.FX": u"人民币",
            "AU(T+D).SGE": u"黄金",
            "B.IPE": u"原油",
            "CA.LME": u"铜",
            "VIX.GI": u"期权"
            }
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
ASSETS_REV_NAME = {value: key for key, value in ASSETS_NAME.iteritems()}
regression_algorithms = ["LinearRegression", "KernelRidgeRegression", "SupportVectorRegression", "Ridge",
                         "RandomForestRegression", "AdaBoostRegression"]
asset_selections = ASSETS_NAME.values()

source = ColumnDataSource(data=dict(date=[], vol=[]))
source_train = ColumnDataSource(data=dict(date=[], pred=[]))
source_test = ColumnDataSource(data=dict(date=[], pred=[]))
source_pred = ColumnDataSource(data=dict(date=[], pred=[]))

def update_data():
    asset_code = ASSETS_REV_NAME[asset_select.value]
    train_date = utils.time2start_date(time_train.value)
    test_date = utils.time2start_date(time_test.value)

    plot.title.text = u"计算中..."
    dataframe, train_df, test_df, pred_df = volatility.get_volatility(asset_code,
                                            key_word=KEY_WORD[asset_code],
                                            model=algorithm_select.value,
                                            train_date=train_date,
                                            test_date=test_date)
    plot.title.text = asset_select.value + u"波动率"

    source.data = {'date': dataframe.index,
                   'vol': dataframe['vol'].values}
    source_train.data = {'date': train_df.index,
                         'pred': train_df['pred'].values}
    source_test.data = {'date': test_df.index,
                        'pred': test_df['pred'].values}
    source_pred.data = {'date': pred_df.index,
                        'pred': pred_df['pred'].values}

tools = "pan,wheel_zoom,box_select,reset"
plot = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot.line('date', 'vol', source=source, line_width=3, line_alpha=0.6, legend=u'实际波动率')
plot.line('date', 'pred', source=source_train, line_width=3, line_alpha=0.6, color='green', legend=u'样本内预测波动率')
plot.line('date', 'pred', source=source_test, line_width=3, line_alpha=0.6, color='red', legend=u'样本外预测波动率')
plot.line('date', 'pred', source=source_pred, line_width=3, line_alpha=0.6, color='red')
plot.title.text_font_size = "15pt"
plot.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot.yaxis.minor_tick_line_color = None
plot.title.text_font = "Microsoft YaHei"

asset_select = Select(value=u"万得全A指数", title=u"资产", width=300, options=asset_selections)
asset_select.on_change('value', lambda attr, old, new: update_data())
algorithm_select = Select(value=regression_algorithms[0], title=u"算法", width=300, options=regression_algorithms)
algorithm_select.on_change('value', lambda attr, old, new: update_data())
time_train = TextInput(value="2016-03-01", title=u"开始训练时间", width=300)
time_train.on_change('value', lambda attr, old, new: update_data())
time_test = TextInput(value="2017-01-01", title=u"开始预测时间（例如：20170101或2017-01-01）", width=300)
time_test.on_change('value', lambda attr, old, new: update_data())
# text = PreText(text=u"""波动率预测模型使用了如下数据作为预测指标：
# 1. 短周期波动率
# 2. 长周期波动率
# 3. 万得全A PE
# 4. 中债指数收益率的倒数
# 5. 日元兑人民币短周期波动率
# 6. 中国波动率指数
# """, height=200, width=1000)

update_data()

select = column(time_train, time_test, row(asset_select, algorithm_select))
inputs = select

curdoc().add_root(column(inputs, plot))
curdoc().title = u"波动率预测"
