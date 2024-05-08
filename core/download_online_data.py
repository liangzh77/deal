from core.stock_io import stock_io, IOSource
from core.tool import *
import os
import numpy as np

sio = stock_io(IOSource.Online)

if 0:
#    用  pro.fund_nav(ts_code='006947.OF')['accum_nav']  获得基金行情，先查code，如果是基金，则调用fund_nav，否则调用pro_bar或daily
    pass

if 1:
    # 下载指数
    fn = 'settings/指数.txt'
    with open(fn, 'r', encoding='utf-8') as f:
        ls = f.readlines()
    #    before = True
    for i in range(1, len(ls)):
        line = ls[i]
        strs = line.split(',')
        code = strs[0]
        #        if code == '006475.OF':
        #            before=False
        #        if before:
        #            continue
        #if os.path.exists('data/' + code):
        #    continue
        for j in range(3):
            try:
                stock = sio.read_stock(ts_code=code, asset='I', freq='D')
                if stock is None or stock.length() == 0:
                    continue
                sio.write_stock(stock)
                print('saved ' + code)
                break
            except Exception as r:
                if '最多访问' in str(r):
                    print('sleep 10 secs, %s' % (r))
                    j -= 1
                    time.sleep(10)

if 0:
    #下载基金
    fn = 'settings/基金.txt'
    with open(fn, 'r', encoding='utf-8') as f:
        ls = f.readlines()
#    before = True
    for i in range(1, len(ls)):
        line = ls[i]
        strs = line.split(',')
        code = strs[0]
#        if code == '006475.OF':
#            before=False
#        if before:
#            continue
#        if os.path.exists('data/'+code):
#            continue
        for j in range(3):
            try:
                stock = sio.read_stock(ts_code=code, asset='I', freq='D')
                if stock is None or stock.length()==0:
                    continue
                sio.write_stock(stock)
                print('saved '+code)
                break
            except Exception as r:
                if '最多访问' in str(r):
                    print('sleep 10 secs, %s'%(r))
                    j -= 1
                    time.sleep(10)

if 0:
    #写基金列表
    keys, ls = sio.fund_list()
    fn = 'settings/基金.txt'
    start_date = '20200101'
    with open(fn,'w',encoding='utf-8') as f:
        l=''
        for i in range(len(keys)):
            l += keys[i]+','
        if len(l)>0:
            l=l[:-1]
        f.write(l+'\n')
        for line in ls:
            if line[5] is None:
                continue
            if line[5]>start_date:
                continue
            if line[6] is None:
                line[6] = ''
            line[6]=line[6].replace(',', '，')
            l=''
            for i in range(len(line)):
                if type(line[i]) != str:
                    l += ','
                else:
                    l += line[i]+','
            if len(l)>0:
                l=l[:-1]
            f.write(l+'\n')

if 0:
    #写A股个股列表
    keys, ls = sio.stock_list()
    fn = 'settings/A股个股.txt'
    with open(fn,'w',encoding='utf-8') as f:
        l=''
        for i in range(len(keys)):
            l += keys[i]+','
        if len(l)>0:
            l=l[:-1]
        f.write(l+'\n')
        for line in ls:
            l=''
            for i in range(len(line)):
                if type(line[i]) != str:
                    l += ','
                else:
                    l += line[i]+','
            if len(l)>0:
                l=l[:-1]
            f.write(l+'\n')

if 0:
    #写个股数据
    #fn = 'settings/a股个股.txt'
    fn = 'settings/基金.txt'
    with open(fn, 'r', encoding='utf-8') as f:
        ls = f.readlines()
#    before = True
    batch = 1
    code = ''
    num_code = 0
    for i in range(1,len(ls)):
        line = ls[i]
        strs = line.split(',')
#        if before and '000032.SZ' not in strs[0]:
#            continue
#        before = False
        if code != '':
            code += ','
        code += strs[0]
        num_code += 1
        if num_code == batch or i==len(ls)-1:
            stocks = sio.read_stock(ts_code=code, freq='D')
            code = ''
            num_code = 0
            sio.write_stock(stocks)

if 0: # 修改个股储存顺序的错误
    def rearange_data(d):
        len = d.shape[0]
        if len > 5000:
            len2 = len - 5000
            d1 = d[:len2][::-1]
            d2 = d[len2:][::-1]
            d = np.hstack((d1,d2))
        else:
            d = d[::-1]
        return d

    sio = stock_io(IOSource.File)
    fn = 'settings/a股个股.txt'
    with open(fn,'r',encoding='utf-8') as f:
        lines = f.readlines()
        for l in lines[1:]:
            strs = l.split(',')
            stock = sio.read_stock(ts_code=strs[0], freq='D')
            stock.times = rearange_data(stock.times)
            stock.opens = rearange_data(stock.opens)
            stock.closes = rearange_data(stock.closes)
            stock.highs = rearange_data(stock.highs)
            stock.lows = rearange_data(stock.lows)
            stock.volume = rearange_data(stock.volume)
            stock.amount = rearange_data(stock.amount)

            sio.write_stock(stock)