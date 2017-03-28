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
import momentum
import price
import const
import cost

ASSETS_NAME = {"881001.WI": u"万得全A指数",
                "HSI.HI": u"恒生指数",
                "SPX.GI": u"标普500",
                "SX5P.GI": u"欧洲50",
                "065.CS": u"中债新综合财富指数",
                "SPGSCITR.SPI": u"商品总指数",
                "USDX.FX": u"美元指数",
                "USDCNY.FX": u"美元兑人民币",
                "AU9999.SGE": u"黄金9999（民生银行）",
                "B.IPE": u"WTI原油",
                "CA.LME": u"LME铜",
                "VIX.GI": u"隐含波动率指数"}
DEPARTMENT_NAME = {'881001': u'万得全A',
                   '000300': U'沪深300',
                   '000905': u'中证500',
                   '399005': u'中小板',
                   '399006': u'创业板'}
INDUSTRY_NAME = {'CI005001.WI': u'石油石化', 'CI005002.WI': u'煤炭', 'CI005003.WI': u'有色金融',
                 'CI005004.WI': u'电力及公用事业', 'CI005005.WI': u'钢铁', 'CI005006.WI': u'基础化工',
                 'CI005007.WI': u'建筑', 'CI005008.WI': u'建材', 'CI005009.WI': u'轻工制造',
                 'CI005010.WI': u'机械', 'CI005011.WI': u'电力设备', 'CI005012.WI': u'国防军工',
                 'CI005013.WI': u'汽车', 'CI005014.WI': u'商贸零售', 'CI005015.WI': u'餐饮旅游',
                 'CI005016.WI': u'家电', 'CI005017.WI': u'纺织服装', 'CI005018.WI': u'医药',
                 'CI005019.WI': u'食品饮料', 'CI005020.WI': u'农林牧渔', 'CI005021.WI': u'银行',
                 'CI005022.WI': u'非银行金融', 'CI005023.WI': u'房地产', 'CI005024.WI': u'交通运输',
                 'CI005025.WI': u'电子元器件', 'CI005026.WI': u'通信', 'CI005027.WI': u'计算机',
                 'CI005028.WI': u'传媒', 'CI005029.WI': u'综合'}
COLORS = Spectral9
COLORS += ["#053061", "#2166ac", "#4393c3"] # "#92c5de", "#d1e5f0", "#f7f7f7", "#fddbc7", "#f4a582", "#d6604d", "#b2182b"]
ASSETS_NAME = {key: value for key, value in ASSETS_NAME.iteritems()}
ASSETS_REV_NAME = {value: key for key, value in ASSETS_NAME.iteritems()}
ASSETS_COLOR = {asset: COLORS[i] for i, asset in enumerate(ASSETS_NAME.values())}
DEPARTMENT_REV_NAME = {value: key for key, value in DEPARTMENT_NAME.items()}
INDUSTRY_REV_NAME = {value: key for key, value in INDUSTRY_NAME.items()}
asset_selections = ASSETS_NAME.values()
index_selections = DEPARTMENT_NAME.values()
industry_seletions = INDUSTRY_NAME.values()

source_price = ColumnDataSource(data=dict(date=[], close=[]))
source_sharpe = ColumnDataSource(data=dict(left=[], right=[], top=[], bottom=[], text=[], sharpe=[], color=[], text_pos=[]))
source_vol = ColumnDataSource(data=dict(days=[], vol=[], max=[], min=[], median=[], percent_75=[], percent_25=[]))
source_cor = ColumnDataSource(data=dict(days=[], cor=[], max=[], min=[], median=[], percent_75=[], percent_25=[]))
source_mom = ColumnDataSource(data=dict(date=[], mom5=[], mom20=[], mom60=[], mom40=[]))
# source_cost = ColumnDataSource(data=dict(left=[], right=[], turnover=[]))
source_turnover_cost = ColumnDataSource(data=dict(date=[], cost=[], mean=[], zero=[]))
source_turnover_cost_text = ColumnDataSource(data=dict(text_x=[], text_y=[], text=[]))
source_cost_stock = ColumnDataSource(data=dict(date=[], cost=[], price=[]))

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
    update_momentum()
    plot_vol.title.text = asset_select.value + u"波动率锥"
    plot_mom.title.text = asset_select.value + u"动量"

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

def update_momentum():
    start_date = time2start_date(time_text.value)
    end_date = time2start_date(time_end_text.value)
    symbol = ASSETS_REV_NAME[asset_select.value]

    data_df = momentum.get_dataframe(symbol, start_date, end_date)
    source_mom.data = source_mom.from_df(data_df)

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

def update_cost():
    """
    date = cost_time_text.value
    fname = "%s/%s.xlsx"%(const.BY_DATE_DIR, date)
    if not os.path.exists(fname):
        plot_cost.title.text = u"该天不是交易日"
    else:
        df = pd.read_excel(fname, index_col=0)
        df["count"] = 1
        count_df = df.groupby("turnover days")["count"].sum()
        source_cost.data = {"left": count_df.index.values - 0.5,
                        "right": count_df.index.values + 0.5,
                        "turnover": count_df.values * 1.0 / count_df.sum()}

        plot_cost.title.text = u"100%换手天数"
    """

    index_code = DEPARTMENT_REV_NAME[department_select.value]
    plot_cost.title.text = u"计算中..."
    print index_code
    cost.cal_market_cost(index_code)
    plot_cost.title.text = department_select.value + u"持有成本盈亏"
    fname = "%s/%s.xlsx"%(const.DATA_DIR, index_code)
    market_df = pd.read_excel(fname, index_col=0)
    market_df = market_df[market_df.index >= "2016-03-01"]
    market_df["mean"] = market_df["current return"].mean()
    market_df["zero"] = 0
    last_value, mean_value = market_df["current return"][-1], market_df["mean"][-1]
    dev_value = (market_df["current return"][-1] - mean_value) / market_df["current return"].std()
    source_turnover_cost.data = {"date": market_df.index.values,
                                 "cost": market_df["current return"].values,
                                 "mean": market_df["mean"].values,
                                 "zero": market_df["zero"].values}
    if last_value > mean_value:
        text_y = [mean_value + 0.02, mean_value, mean_value - 0.02]
    else:
        text_y = [last_value, last_value + 0.02, last_value - 0.02]
    source_turnover_cost_text.data = {"text_x": [market_df.index[-1]]*3,
                                      "text_y": text_y,
                                      "text": [u"当前值: %.2f%%"%(last_value*100), u"历史均值: %.2f%%"%(mean_value*100),
                                               u"偏离均值%.2f个标准差"%(dev_value)]}

def update_cost_industry():
    index_code = INDUSTRY_REV_NAME[industry_select.value]
    plot_cost.title.text = u"计算中..."
    print index_code
    cost.cal_market_cost(index_code)
    plot_cost.title.text = industry_select.value + u"持有成本盈亏"
    fname = "%s/%s.xlsx"%(const.DATA_DIR, index_code)
    market_df = pd.read_excel(fname, index_col=0)
    market_df = market_df[market_df.index >= "2016-03-01"]
    market_df["mean"] = market_df["current return"].mean()
    market_df["zero"] = 0
    last_value, mean_value = market_df["current return"][-1], market_df["mean"][-1]
    dev_value = (market_df["current return"][-1] - mean_value) / market_df["current return"].std()
    source_turnover_cost.data = {"date": market_df.index.values,
                                 "cost": market_df["current return"].values,
                                 "mean": market_df["mean"].values,
                                 "zero": market_df["zero"].values}
    if last_value > mean_value:
        text_y = [mean_value + 0.02, mean_value, mean_value - 0.02]
    else:
        text_y = [last_value, last_value + 0.02, last_value - 0.02]
    source_turnover_cost_text.data = {"text_x": [market_df.index[-1]]*3,
                                      "text_y": text_y,
                                      "text": [u"当前值: %.2f%%"%(last_value*100), u"历史均值: %.2f%%"%(mean_value*100),
                                               u"偏离均值%.2f个标准差"%(dev_value)]}

def update_cost_stock():
    stock = stock_select.value
    fname = "%s/%s.xlsx"%(const.BY_STOCK_DIR, stock)
    if not os.path.exists(fname):
        plot_cost_stock.title.text = u"该股不在数据库中"
    else:
        df = pd.read_excel(fname, index_col=0)
        df.index = pd.to_datetime(df.index, format="%Y-%m-%d")
        source_cost_stock.data = {"date": df.index,
                                  "cost": df["avg cost"].values,
                                  "price": df["close"].values}
        plot_cost_stock.title.text = stock_select.value + u"持有成本与价格"

def update_all():
    update_data()
    update_statistics()
    update_correlation()
    update_cost()
    update_cost_stock()

asset_select = Select(value=u"标普500", title="资产", width=300, options=asset_selections)
asset_select.on_change('value', lambda attr, old, new: update_data())
time_text = TextInput(value="2002-01-01", title="开始时间（例如：20050101或2005-01-01）", width=300)
time_text.on_change('value', lambda attr, old, new: update_all())
# cost_time_text = TextInput(value="2017-03-14", title=u"时间", width=300)
# cost_time_text.on_change('value', lambda attr, old, new: update_cost())
today = datetime.datetime.today()
time_end_text = TextInput(value=today.strftime("%Y-%m-%d"), title="终止时间", width=300)
time_end_text.on_change('value', lambda attr, old, new: update_all())
asset_text_1 = TextInput(value="881001.WI", title=u"资产一（万得代码）", width=300)
asset_text_2 = TextInput(value="HSI.HI", title=u"资产二（万得代码）", width=300)
department_select = Select(value=u"万得全A", title=u"选择板块", width=300, options=index_selections)
department_select.on_change('value', lambda attr, old, new: update_cost())
industry_select = Select(value=u"石油石化", title=u"选择行业", width=300, options=industry_seletions)
industry_select.on_change('value', lambda attr, old, new: update_cost_industry())
stock_select = TextInput(value="000001.SZ", title=u"选择股票", width=300)
stock_select.on_change('value', lambda attr, old, new: update_cost_stock())

tools = "pan,wheel_zoom,box_select,reset"
plot_price = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_price.title.text_font_size = "15pt"
plot_price.yaxis.minor_tick_line_color = None
plot_price.title.text_font = "Microsoft YaHei"

plot_mom = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_mom.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_mom.title.text_font_size = "15pt"
plot_mom.yaxis.minor_tick_line_color = None
plot_mom.title.text_font = "Microsoft YaHei"
plot_mom.line('date', 'mom5', source=source_mom, line_width=2, color='red', legend=u'5日动量')
plot_mom.line('date', 'mom20', source=source_mom, line_width=2, color='yellow', legend=u'一个月动量')
plot_mom.line('date', 'mom40', source=source_mom, line_width=2, color='green', legend=u'两个月动量')
plot_mom.line('date', 'mom60', source=source_mom, line_width=2, color='blue', legend=u'三个月动量')

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

plot_cost = figure(plot_height=400, plot_width=1000, tools=tools, title=u"万得全A持有成本盈亏", x_axis_type="datetime")
# plot_cost.quad(left='left', right='right', bottom=0, top='turnover', source=source_cost, fill_color="#036564", line_color="#033649")
plot_cost.text(x='text_x', y='text_y', text='text', source=source_turnover_cost_text, text_font_size='9pt')
plot_cost.line('date', 'cost', source=source_turnover_cost, line_width=3, legend=u"当前盈亏")
plot_cost.line('date', 'mean', source=source_turnover_cost, line_width=2, color='#33FF66', legend=u"盈亏均值")
plot_cost.line('date', 'zero', source=source_turnover_cost, line_width=2, color='red', legend=u"零")
plot_cost.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_cost.yaxis.axis_label = u"percentage"
plot_cost.title.text_font_size = "15pt"
plot_cost.yaxis.minor_tick_line_color = None

plot_cost_stock = figure(plot_height=400, plot_width=1000, tools=tools, title=u"000001.SZ持有成本与价格", x_axis_type="datetime")
# plot_cost.quad(left='left', right='right', bottom=0, top='turnover', source=source_cost, fill_color="#036564", line_color="#033649")
plot_cost_stock.line('date', 'cost', source=source_cost_stock, line_width=3, legend=u"成本")
plot_cost_stock.line('date', 'price', source=source_cost_stock, line_width=2, color='red', legend=u"价格")
plot_cost_stock.title.text_font_size = "15pt"
plot_cost_stock.yaxis.minor_tick_line_color = None

plot_blank = figure(plot_height=400, plot_width=1000, tools=[])

update_all()

asset_text_1 = TextInput(value="881001.WI", title=u"资产一", width=300)
asset_text_2 = TextInput(value="HSI.HI", title=u"资产二", width=300)
update_button = Button(label=u"计算相关性", width=300, button_type="success")
update_button.on_click(update_correlation)
asset_row = row(asset_text_1, asset_text_2, update_button)
department_industry_row = row(department_select, industry_select)

inputs = widgetbox(time_text, time_end_text, asset_select)

curdoc().add_root(column(inputs, plot_sharpe, plot_price, plot_mom, plot_vol, asset_row, plot_correlation,
                         department_industry_row, plot_cost, stock_select, plot_cost_stock, plot_blank))
curdoc().title = u"每日资产总结"
