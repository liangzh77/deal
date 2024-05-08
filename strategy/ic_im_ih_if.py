import cv2
import numpy as np
from core.stock_io import stock_io, IOSource
from draw.stock_draw import Stock_draw
from tkinter import Tk,StringVar,DoubleVar,Entry,W,Radiobutton,Listbox,Button
from tkinter.ttk import Combobox,Label
from PIL import Image, ImageTk
import os
import time
import math
from filter import filter_list
from core.tool import *

def clear_all_but_closes(s):
    s.opens=np.zeros(0)
    s.highs=np.zeros(0)
    s.lows=np.zeros(0)
    s.volume=np.zeros(0)
    s.amount=np.zeros(0)

codes = {'ic': '399905.SZ', 'im': '000852.SH', 'ih': '000016.SH', 'if': '399300.SZ'}
#codes = {'im': '000852.SH', 'ih': '000016.SH'}
multiplier = {'ic': 200, 'im': 200, 'ih': 300, 'if': 300}
sio = stock_io(IOSource.File)
if os.path.exists('cache/'+list(codes.keys())[0]) is False:
    sd = None
    for name in codes:
        code = codes[name]
        stock = sio.read_stock(code, freq='D')
        stock.name = name
        clear_all_but_closes(stock)
        if sd is None:
            sd = Stock_draw(stock, 0, 0, -1)
        else:
            sd.add_stock(stock)
    sio.write_stock(sd.stock,'cache/'+sd.stock.name)
    for stock in sd.stocks:
        sio.write_stock(stock, 'cache/' + stock.name)
    print('data saved to cache')

stocks = {}
for name in codes:
    code = codes[name]
    stock = sio.read_stock('cache/'+name, freq='D')
    stocks[name] = stock

# 参数
baseline_win = 200
start = -4294
end = start+4294
low_thresh = -10
#cur_low_dif = 10

#基础收益率
for name in stocks:
    s = stocks[name]
    gain = (s.closes[end-1]-s.closes[start])*multiplier[name]
    print('基础收益：{}，{}万'.format(name,int(gain/10000)))

# 去基线，归一化振幅
stocks2 = {}
for name in stocks:
    s = stocks[name].clone()
    s.closes *= multiplier[name] / 10000
    remove_baseline(s, baseline_win)
    #normalize_amplitude(s,22)
    stocks2[name] = s

num_stock = len(stocks)
for i in range(s.length()):
    mean_val = 0
    for s in stocks2.values():
        mean_val+=s.closes[i]
    mean_val/=num_stock
    for s in stocks2.values():
        s.closes[i] -= mean_val

def find_low(ss,ind):
    low=1e10
    name = ''
    for n in ss:
        s2 = ss[n]
        if s2.closes[ind]<low:
            low = s2.closes[ind]
            name = n
    return low, name

def find_high(ss,ind):
    high=-1e10
    name = ''
    for n in ss:
        s2 = ss[n]
        if s2.closes[ind]>high:
            high = s2.closes[ind]
            name = n
    return high, name

# 遍历
time_struct = time.localtime(stocks2[name].times[start])
time_str_from = time.strftime("%Y-%m-%d", time_struct)
time_struct = time.localtime(stocks2[name].times[end-1])
time_str_end = time.strftime("%Y-%m-%d", time_struct)
print('从{}到{}'.format(time_str_from,time_str_end))
gain2=0
#low, name = find_low(stocks2, start)
cur_name = ''
buy_short=False
buy_short_start_gain = 0
idling = False
idle_start_ind = 0
for i in range(start, end-1):
    #cur_val = stocks2[cur_name].closes[i]
    low, name = find_low(stocks2, i)
    time_struct = time.localtime(stocks2[name].times[i])
    time_str = time.strftime("%Y-%m-%d", time_struct)
    #if low<cur_val-cur_low_dif:
    #if cur_val>1:
    if name!=cur_name and low<low_thresh:
        print('{},from [{}] to [{}]'.format(time_str,cur_name,name))
        cur_name = name
    if cur_name!='' and idling is False:
        if cur_name=='im' or cur_name=='ic':
            gain2 += (stocks[cur_name].closes[i+1]-stocks[cur_name].closes[i])*multiplier[cur_name]
            buy_short = False
        else:
            if low<-7:
#            if stocks2['im'].closes[i]>9:
                if buy_short is False:
                    buy_short = True
                    buy_short_start_gain = gain2
                gain2 -= (stocks['im'].closes[i+1]-stocks['im'].closes[i])*multiplier['im']
                if gain2<buy_short_start_gain-200000:
                    idling = True
                    idle_start_ind = i
                    print('{},start idling'.format(time_str))
            else:
                gain2 += (stocks['im'].closes[i + 1] - stocks['im'].closes[i]) * multiplier['im']
    if idling:
        if i>idle_start_ind+22:
            buy_short = False
            idling = False
            print('{},stop idling'.format(time_str))

print('做多收益：{}万'.format(int(gain2/10000)))
