import time
import datetime
import math
import numpy as np
from core.stock import Stock

def str2ts(s, fm):
    return int(time.mktime(time.strptime(s, fm)))

def ts2str(ts, fm):
    return datetime.datetime.fromtimestamp(ts).strftime(fm)#"%Y-%m-%d %H:%M:%S")

def float_to_str(v, valid_num):
    if v==0:
        return '0'
    str_start = ''
    if v<0:
        str_start = '-'
        v=-v
    str_end = ''
    logv = math.log(v,10)
    if logv>9:
        v /= 1e9
        str_end = 'G'
    elif logv>6:
        v /= 1e6
        str_end = 'M'
    elif logv>3:
        v /= 1e3
        str_end = 'K'

    logv = math.log(v,10)
    if logv > 3:
        newv = int(round(v))
        return str_start+str(newv)+str_end
    if logv > 2:
        newv = int(v * 10) / 10
        return str_start+str(newv)+str_end
    elif logv > 1:
        newv = int(v * 100) / 100
        return str_start + str(newv) + str_end
    elif logv > 0:
        newv = int(v * 1000) / 1000
        return str_start + str(newv) + str_end
    else:
        tmp = int(np.floor(logv))
        newv = int(v * math.pow(10,-tmp+2)) / math.pow(10,-tmp+2)
        return str_start + str(newv) + str_end

def remove_baseline(stock, win=5):
    ma = stock.ma(win)
    if ma.shape[0]>=win:
        ma[:win-1]=ma[win-1]
    for i in range(stock.length()):
        stock.closes[i] -= ma[i]

def normalize_amplitude_old(stock, win=0):
    if win==0 or win>stock.length():
        win=stock.length()
    c = np.abs(stock.closes[-win:])
    c.sort()
    if c.shape[0]>0:
        v = c[int(c.shape[0]*0.9)]
        stock.closes = stock.closes / v

def normalize_amplitude(stock, win=0):
    if win==0 or win>stock.length():
        win=stock.length()
    close_abs = np.abs(stock.closes)
    mean_ca = np.mean(close_abs[:win])
    for i in range(win):
        stock.closes[i] /= mean_ca
    for i in range(win,stock.length()):
        stock.closes[i] /= np.mean(close_abs[i+1-win:i+1])

def load_all_codes(data_sources):
    all_codes = {}
    for source in data_sources:
        with open('settings/' + source + '.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            stock_keys = []
            if len(lines) > 0 and len(lines[0]) > 0:
                l = lines[0]
                if l[-1] == '\n':
                    l = l[:-1]
                    stock_keys = l.split(',')[1:]
                for l in lines[1:]:
                    if len(l) == 0:
                        continue
                    if l[-1] == '\n':
                        l = l[:-1]
                    strs = l.split(',')
                    param = {}
                    if len(strs) > len(stock_keys) + 1:
                        a = 1
                    for i in range(1, len(strs)):
                        param[stock_keys[i - 1]] = strs[i]
                    all_codes[strs[0].upper()] = param
    return all_codes