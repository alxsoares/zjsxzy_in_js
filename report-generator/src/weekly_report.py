# encoding: utf-8

import pandas as pd
import numpy as np
from WindPy import w

import const
import utils

def get_all_dataframe(fname):
    all_df = pd.read_excel(fname, sheetname=None)
    return all_df

# 指数周数据
def index_data(index_df):
    index_df = index_df.set_index(u'证券代码')
    index_df[u'涨跌'] = index_df[u'涨跌幅'].map(lambda x: utils.change(x))
    # 债券重命名
    index_df[u'证券简称'] = index_df[u'证券简称'].map(lambda x: x.replace(u'财富(总值)', '').replace(u'总', ''))
    index_df['content'] = ''
    for index in index_df.index:
        index_df.loc[index, 'content'] = u'%s%s，收于%.2f点'%(
                    index_df.loc[index, u'证券简称'], index_df.loc[index, u'涨跌'], index_df.loc[index, u'收盘'])
    content = []
    content.append(oversea_stock_market(index_df))
    content.append(domestic_stock_market(index_df))
    content.append(bond_market(index_df))
    content.append(commodity_market(index_df))
    with open(u'%s/市场回顾.txt'%(const.DESKTOP_DIR), 'w') as f:
        f.write('\n'.join(content).encode('utf-8'))

# 海外市场
def oversea_stock_market(index_df):
    content = u'本周海外股市：标普%s；伦敦%s；%s；%s；%s。'%(
            index_df.loc['SPX.gi', 'content'],
            index_df.loc['FTSE.GI', 'content'],
            index_df.loc['GDAXI.GI', 'content'],
            index_df.loc['N225.GI', 'content'],
            index_df.loc['HSI.HI', 'content'])
    return content

# 国内市场
def domestic_stock_market(index_df):
    content = u'国内股市：%s；%s；%s；%s。'%(
            index_df.loc['000001.SH', 'content'],
            index_df.loc['399001.SZ', 'content'],
            index_df.loc['399005.SZ', 'content'],
            index_df.loc['399006.SZ', 'content'])
    return content

# 固定收益市场
def bond_market(index_df):
    content = u'%s；%s；%s；%s。'%(
            index_df.loc['045.CS', 'content'],
            index_df.loc['066.CS', 'content'],
            index_df.loc['053.CS', 'content'],
            index_df.loc['057.CS', 'content'])
    return content

# 大宗商品市场
def commodity_market(index_df):
    content = u'%s；%s；%s；%s。'%(
            index_df.loc['CRBSA.RB', 'content'],
            index_df.loc['CRBRI.RB', 'content'],
            index_df.loc['CRBMS.RB', 'content'],
            index_df.loc['CRBFO.RB', 'content'])
    return content

def change_position(inv1_df, inv2_df, columns, string):
    col_name = u'占净值比例'
    elements = []
    for col in columns:
        num = (inv2_df.loc[col, col_name] - inv1_df.loc[col, col_name])*100
        if not np.isnan(num) and np.abs(num) > 0.01:
            line = u'%s%s'%(utils.up_down(num), col)
            elements.append(line)
    string += u'；'.join(elements)
    return string

# 基金持仓
def fund_position(df):
    col_name = u'市值占净值'
    hk, gold, bond, astock, oversea_stock, money = 0, 0, 0, 0, 0, 0
    for index in df.index:
        name = df.loc[index, u'名称']
        ftype = df.loc[index, 'type']
        percent = df.loc[index, col_name]
        if utils.hk_fund_name(name):
            hk += percent
        elif utils.gold_fund_name(name):
            gold += percent
        elif utils.money_fund_type(ftype) or utils.money_fund_name(name):
            money += percent
        elif utils.oversea_fund_type(ftype):
            oversea_stock += percent
        elif utils.bond_fund_type(ftype):
            bond += percent
        else:
            astock += percent
    return astock, hk, gold, money, oversea_stock, bond

# 本周投资情况分析
def investment_analysis(inv1_df, inv2_df, fund1_df, fund2_df):
    inv1_df.index = inv1_df.index.map(lambda x: x.strip())
    inv2_df.index = inv2_df.index.map(lambda x: x.strip())

    content = []
    hk1, astock1, gold1, money1, oversea_stock1, bond1 = fund_position(fund1_df)
    hk2, astock2, gold2, money2, oversea_stock2, bond2 = fund_position(fund2_df)
    line = money_management(inv1_df, inv2_df)
    num = (money2 - money1) * 100
    if abs(num) > 0.001:
        line += u"；%s货币基金"%(utils.up_down(num))
    content.append(line)
    line = fixed_income_management(inv1_df, inv2_df)
    num = (bond2 - bond1) * 100
    if abs(num) > 0.001:
        line += u"；%s债券基金"%(utils.up_down(num))
    content.append(line)
    line = finance_management(inv1_df, inv2_df)
    content.append(line)
    line = u'权益方面：'
    elements = []
    num = (astock2 - astock1) * 100
    if abs(num) > 0.001:
        elements.append(u'%sA股配置'%(utils.up_down(num)))
    num = (hk2 - hk1) * 100
    if abs(num) > 0.001:
        elements.append(u'%s港股配置'%(utils.up_down(num)))
    num = (oversea_stock2 - oversea_stock1) * 100
    if abs(num) > 0.001:
        elements.append(u'%s海外股票配置'%(utils.up_down(num)))
    line += u'；'.join(elements)
    content.append(line)
    line = u'商品方面：%s黄金'%(utils.up_down((gold2-gold1)*100))
    content.append(line)
    with open(u'%s/本周投资情况分析.txt'%(const.DESKTOP_DIR), 'w') as f:
        f.write('\n'.join(content).encode('utf-8'))

# 现金管理
def money_management(inv1_df, inv2_df):
    columns = [u'活期存款', u'定期存款', u'拆借存款']
    string = u'现金管理：'
    content = change_position(inv1_df, inv2_df, columns, string)
    return content

# 固定收益
def fixed_income_management(inv1_df, inv2_df):
    columns = [u'国债',
               u'央票',
               u'政策性金融债',
               u'非政策性金融债',
               u'短融(含超短融)',
               u'中期票据',
               u'企业债(不含短融和中票)',
               u'公司债',
               u'可转债',
               u'资产支持证券',
               u'地方政府债',
               u'可交换债',
               u'定期存单',
    ]
    string = u'固定收益：'
    content = change_position(inv1_df, inv2_df, columns, string)
    return content

# 融资融券
def finance_management(inv1_df, inv2_df):
    columns = [u'融资', u'融券']
    string = u'融资融券：'
    content = change_position(inv1_df, inv2_df, columns, string)
    return content

# 本期末账户状态
def current_position(inv2_df, fund2_df, hold_df):
    hk2, astock2, gold2, money2, oversea_stock2, bond2 = fund_position(fund2_df)

    content = []
    net_price = inv2_df.loc[u'资产总净值', u'市值（亿）']
    line = u'专户资产规模：%.4f亿元'%(net_price)
    content.append(line)
    if inv2_df.loc[u'债券', u'占净值比例'] > 0:
        bond2 += inv2_df.loc[u'债券', u'占净值比例']
    line = u'固收配置规模：%.2f亿元'%(net_price*bond2)
    content.append(line)
    line = u'权益类配置规模：%.2f亿元'%(net_price*(astock2+hk2))
    content.append(line)
    line = u'大宗商品配置规模：%.2f亿元'%(net_price*(gold2))
    content.append(line)
    if inv2_df.loc[u'存款', u'占净值比例'] > 0:
        money2 += inv2_df.loc[u'存款', u'占净值比例']
    line = u'现金类配置规模：%.2f亿元'%(net_price*money2)
    content.append(line)
    line = u'杠杆率：100%'
    content.append(line)
    line = u'今年以来收益：%.2f%%'%(hold_df.iloc[-1][u'累计收益率（%） ']*100)
    content.append(line)
    with open(u'%s/本期末账户状态.txt'%(const.DESKTOP_DIR), 'w') as f:
        f.write('\n'.join(content).encode('utf-8'))

if __name__ == '__main__':
    excel_fname = u'%s/%s/%s'%(const.WEEK_DATA_DIR, '20170605', u'稳进5号.xlsx')
    all_df = get_all_dataframe(excel_fname)
    index_df = all_df[u'指数']
    inv1_df = all_df[u'日报1']
    inv2_df = all_df[u'日报2']
    fund1_df = all_df[u'基金持仓1']
    fund2_df = all_df[u'基金持仓2']
    hold_df = all_df[u'持仓']
    w.start()
    data = w.wss(fund1_df[u'代码'].tolist(), 'fund_firstinvesttype')
    fund1_df['type'] = data.Data[0]
    data = w.wss(fund2_df[u'代码'].tolist(), 'fund_firstinvesttype')
    fund2_df['type'] = data.Data[0]

    print(u'指数数据')
    index_data(index_df)
    print(u'投资情况')
    investment_analysis(inv1_df, inv2_df, fund1_df, fund2_df)
    print(u'期末状况')
    current_position(inv2_df, fund2_df, hold_df)
