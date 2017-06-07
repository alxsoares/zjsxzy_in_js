# encoding: utf-8
# 关于专户历史持仓结构的报告生成程序

import pandas as pd

import const

def get_history_position_dataframe():
    '''
    得到历史持仓数据
    '''
    df = pd.read_excel(const.HISTORY_POSITION_FILE, index_col=0)
    df = df.sort_index()
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
    df.index = df.index.map(lambda x: x.strftime('%Y-%m-%d'))
    return df

def generate_area_percent_stacked():
    '''
    根据历史持仓生成area percent stacked图

    输入数据：专户历史持仓.xlsx
    输出数据：客户_专户历史持仓.xlsx
    '''
    df = get_history_position_dataframe()
    df = df[const.selected_columns]

    excel_file = u'%s/客户_专户历史持仓.xlsx'%(const.DATA_DIR)
    sheet_name = 'Sheet1'

    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name)
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    # Create a chart object.
    chart = workbook.add_chart({'type': 'area', 'subtype': 'percent_stacked'})

    max_row, max_col = len(df), len(df.columns)
    for i in range(max_col):
        col = i + 1
        chart.add_series({
                'name': ['Sheet1', 0, col],
                'categories': ['Sheet1', 1, 0, max_row, 0],
                'values': ['Sheet1', 1, col, max_row, col],
            })
    chart.set_x_axis({'name': u'日期', 'date_axis': True})
    worksheet.insert_chart(1, max_col+2, chart)
    writer.save()

if __name__ == '__main__':
    generate_area_percent_stacked()
