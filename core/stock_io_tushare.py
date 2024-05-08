from core.stock import Stock
import tushare as ts
import numpy as np
from core.tool import str2ts

pro = ts.pro_api()

def read_stock_online(ts_code, asset='E', start_date='20180101', end_date='20181011', freq='1min'):
    df = ts.pro_bar(ts_code=ts_code, adj='qfq', asset=asset, start_date=start_date, end_date=end_date, freq=freq)
    if df is None or df.shape[0]==0:
        df = pro.fund_nav(ts_code=ts_code)
        if df is not None:
            if 'nav_date' not in df:
                return None
            df['trade_date'] = df['nav_date']
            df['close'] = df['adj_nav']

    if 'trade_time' in df.keys():
        times = np.zeros(df['trade_time'].count(),dtype=np.int64)
        for i in range(df['trade_time'].values.shape[0]):
            times[i] = str2ts(df['trade_time'].values[i],'%Y-%m-%d %H:%M:%S')
    else:
        times = np.zeros(df['trade_date'].count(), dtype=np.int64)
        for i in range(df['trade_date'].values.shape[0]):
            times[i] = str2ts(df['trade_date'].values[i],'%Y%m%d')
    stock = Stock()
    opens=highs=lows=vols=amts=None
    if 'open' in df:
        opens = df['open'].values[::-1]
    if 'high' in df:
        highs = df['high'].values[::-1]
    if 'low' in df:
        lows = df['low'].values[::-1]
    if 'vol' in df:
        vols = df['vol'].values[::-1]
    if 'amount' in df:
        amts = df['amount'].values[::-1]
    stock.set(ts_code, freq, times[::-1],
              opens,
              df['close'].values[::-1],
              highs,
              lows,
              vols,
              amts)
    return stock

def fund_list():
    data = pro.fund_basic(limit=1000000,status='L',fields='ts_code,name,management,custodian,fund_type,found_date,benchmark')
    return data.keys(), data.values

def stock_list():
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    return data.keys(), data.values

def read_stocks_online(ts_code, asset='E', start_date='20180101', end_date='20181011', freq='1min'):
    df = ts.pro_bar(ts_code=ts_code, adj='qfq', asset=asset, start_date=start_date, end_date=end_date, freq=freq)
    if 'trade_time' in df.keys():
        times = np.zeros(df['trade_time'].count(),dtype=np.int64)
        for i in range(df['trade_time'].values.shape[0]):
            times[i] = str2ts(df['trade_time'].values[i],'%Y-%m-%d %H:%M:%S')
    else:
        times = np.zeros(df['trade_date'].count(), dtype=np.int64)
        for i in range(df['trade_date'].values.shape[0]):
            times[i] = str2ts(df['trade_date'].values[i],'%Y%m%d')

    codes = ts_code.split(',')
    timesm = {}
    opensm = {}
    closesm = {}
    highsm = {}
    lowsm = {}
    volumem = {}
    amountm = {}
    for c in codes:
        timesm[c] = []
        opensm[c] = []
        closesm[c] = []
        highsm[c] = []
        lowsm[c] = []
        volumem[c] = []
        amountm[c] = []
    for i in range(df.shape[0]):
        code = df.ts_code[i]
        timesm[code].append(times[i])
        opensm[code].append(df.open[i])
        closesm[code].append(df.close[i])
        highsm[code].append(df.high[i])
        lowsm[code].append(df.low[i])
        volumem[code].append(df.vol[i])
        amountm[code].append(df.amount[i])

    stocks = {}
    for c in codes:
        stock = Stock()
        stock.set(c, freq, np.array(timesm[c]),
                  np.array(opensm[c]), np.array(closesm[c]),
                  np.array(highsm[c]), np.array(lowsm[c]),
                  np.array(volumem[c]), np.array(amountm[c]))
        stocks[c] = stock
    return stocks
