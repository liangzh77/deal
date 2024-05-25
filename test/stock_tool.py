import sys, os, pickle
script_dir = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(script_dir)
base_dir = os.path.split(script_dir)[0]
sys.path.append(base_dir)
from mysql_db.mysql_tool import *
from stock_filter import *


def init_chunk():
    c = {}
    c['timev'] = []
    c['openv'] = []
    c['closev'] = []
    c['low'] = []
    c['high'] = []
    c['volume'] = []
    return c

def squeeze_chunk(c):
    openv = c['closev'][0]
    closev = c['closev'][-1]
    low = min(c['closev'])
    high = max(c['closev'])
    vol = sum(c['volume'])
    return openv, closev, low, high, vol


def append(c, timev, price, volume):
    c['timev'].append(timev)
    c['closev'].append(price)
    c['volume'].append(volume)

def append_full(c, time, open, close, low, high, volume):
    append(c, time, close, volume)
    c['openv'].append(open)
    c['low'].append(low)
    c['high'].append(high)

class Stock:
    def __init__(self, code_info) -> None:
        self.info = {'day':init_chunk(),'min5':{}}
        self.info.update(code_info)
        code = code_info['code']
        sql = f'select * from zyx.{code}'
        self.info['raw_min5'] = query_sql(sql, logging=False)
        self._arange_data()

    def _arange_data(self):
        info = self.info
        for d in info['raw_min5']:
            dt, price, volume = d['datetime'], d['price'], d['volume']
            date1, time1 = dt.split(' ')
            if 'start_date' not in info:
                info['start_date'] = date1
            info['end_date'] = date1
            if date1 not in info['min5']:
                info['min5'][date1] = init_chunk()
            append(info['min5'][date1], time1, price, volume)
        for date1 in info['min5']:
            openv, closev, low, high, vol = squeeze_chunk(info['min5'][date1])
            append_full(info['day'], date1, openv, closev, low, high, vol)
        del info['raw_min5']

    def _calc_daily(self):
        for d in self.min5:
            pass

class Stocks:
    s = {}
    def __getitem__(self, code):
        if code not in self.s:
            with open(f'data/{code}.pkl', 'rb') as f:
                stock = pickle.load(f)
            self.s[code] = stock
        return self.s[code]
    
    def __setitem__(self, code, stock):
        self.s[code] = stock

def load_codes_from_file(fn):
    with open(fn,'r',encoding='utf-8') as f:
        lines = f.readlines()

    codes = {}
    for l in lines[1:]:
        t,_,name,market,industry,_ = l.strip().split(',')
        t2 = t.split('.')
        code = t2[1]+t2[0]
        codes[code] = {'code':code,'name':name,'market':market,'industry':industry}
    return codes


# 从缓存文件加载codes
if 0:
    codes = load_codes_from_file('settings/a股个股.txt')
    for code in codes:
        with open(f'data/{code}.pkl', 'rb') as f:
            stock = pickle.load(f)

# 从数据库加载codes，并写缓存文件
if 0:
    codes = load_codes_from_file('settings/a股个股.txt')
    for code in codes:
        stock = Stock(codes[code])
        with open(f'data/{code}.pkl', 'wb') as f:
            pickle.dump(stock, f)

def temp_save_pkl(v):
    with open(f'temp.pkl', 'wb') as f:
        pickle.dump(v, f)

def temp_load_pkl():
    with open(f'temp.pkl', 'rb') as f:
        return pickle.load(f)

if __name__ == '__main__':
    fn = 'settings/a股个股.txt'
    codes = load_codes_from_file(fn)

    stocks = Stocks()
    codes2 = {key: codes[key] for key in list(codes.keys())[:100]}
#    selected = temp_load_pkl()
    selected = filter_stock4(stocks, codes)
    from stock_evaluate import *
    eval2(selected)
    a=1