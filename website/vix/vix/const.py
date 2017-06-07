DATA_DIR = "C:/Users/jgtzsx01/Documents/workspace/zjsxzy_in_js/website/vix/data"

URLS = {
    'VXFXI': "http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/vxfxidailyprices.csv",
    'VXGDX': "http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/vxgdxdailyprices.csv",
    'OVX': "http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/ovxhistory.csv",
    'VXXLE': "http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/vxxledailyprices.csv",
    'VXEEM': "http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/vxeemdailyprices.csv",
    'GVZ': "http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/gvzhistory.csv",
    'VXSLV': "http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/vxslvdailyprices.csv",
    'EVZ': "http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/evzhistory.csv",
    'TYVIX': "http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/tyvixdailyprices.csv",
    'VXD': 'http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/vxdohlcprices.csv',
    'VXO': 'http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/vxocurrent.csv',
    'RVX': 'http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/rvxdailyprices.csv',
    'VXN': 'http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/vxncurrent.csv',
    'VXEFA': 'http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/vxefadailydata.csv',
}
NAMES = {
    'VXFXI': 'China ETF Volatility Index',
    'VXGDX': 'Gold Miners ETF Volatility Index',
    'OVX': 'Crude Oil ETF Volatility Index',
    'VXXLE': 'Energy Sector ETF Volatility Index',
    'VXEEM': 'Emerging Markets ETF Volatility Index',
    'GVZ': 'Gold ETF Volatility Index',
    'VXSLV': 'Silver ETF Volatility Index',
    'EVZ': 'EuroCurrency ETF Volatility Index',
    'TYVIX': '10-year U.S. Treasury Note Volatility Index',
    'VXD': 'DJIA Volatility Index',
    'VXO': 'S&P 100 Volatility Index',
    'RVX': 'Russell 2000 Volatility Index',
    'VXN': 'NASDAQ-100 Volatility Index',
    'VXEFA': 'EFA ETF Volatility Index',
}
REV_NAMES = {value: key for key, value in NAMES.iteritems()}

start_date = "2012-01-01"
window = 61
