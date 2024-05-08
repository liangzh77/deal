from core.stock import Stock
import numpy as np
from core.tool import str2ts

def read_stock_csv(fn, freq='D'):
    if freq!='D':
        return
    times = []
    opens = []
    closes = []
    highs = []
    lows = []
    volume = []
    amount = []
    with open(fn,'r') as f:
        ls = f.readlines()
        for i in range(len(ls)):
            if ls[i][-1] == '\n':
                ls[i] = ls[i][:-1]
        names={}
        strs = ls[0].split(',')
        for i in range(len(strs)):
            names[strs[i]] = i

        for l in ls[1:]:
            strs = l.split(',')
            times.append(str2ts(strs[names['时间']],'%Y-%m-%d'))
            opens.append(float(strs[names['开盘价']]))
            highs.append(float(strs[names['最高价']]))
            lows.append(float(strs[names['最低价']]))
            closes.append(float(strs[names['收盘价']]))
            volume.append(float(strs[names['成交量']]))
            amount.append(float(strs[names['成交额']]))

        stock = Stock()
        ts_code = fn
        p=ts_code.rfind('.')
        if p>=0:
            ts_code = ts_code[:p]
        ts_code = str.replace(ts_code,'\\','/')
        p = ts_code.rfind('/')
        if p>=0:
            ts_code = ts_code[p+1:]
        stock.set(ts_code,freq,times, opens, closes, highs, lows, volume, amount)
        return stock

if 0:
    stock = read_stock_csv('../data/csv数据/index futures/TS主力连续.csv')
    sio.write_stock(stock)
