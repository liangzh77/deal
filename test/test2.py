import sys, os, pickle
sys.path.append(os.getcwd())
from mysql_db.mysql_tool import *


#sql = 'select * from zyx.sz000001'
#ret = query_sql(sql, logging=False)

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


load_from_file = False
if __name__ == '__main__':
    fn = 'settings/a股个股.txt'
    with open(fn,'r',encoding='utf-8') as f:
        lines = f.readlines()

    codes = {}
    for l in lines[1:]:
        t,_,name,market,industry,_ = l.strip().split(',')
        t2 = t.split('.')
        code = t2[1]+t2[0]
        codes[code] = {'code':code,'name':name,'market':market,'industry':industry}

    stocks = Stocks()
    if 0:
        for code in codes:
            if load_from_file:
                with open(f'data/{code}.pkl', 'rb') as f:
                    stock = pickle.load(f)
            else:
                stock = Stock(codes[code])
                with open(f'data/{code}.pkl', 'wb') as f:
                    pickle.dump(stock, f)

    selected = {}
    for code in codes:
        if code[2:4] in ['30','68']:
            rg = 0.199
        else:
            rg = 0.099
        s = stocks[code]
        day = s.info['day']
        closev = day['closev']
        volume = day['volume']
        amt = [x * y for x, y in zip(closev, volume)]
        for i in range(5,len(amt)):
            if amt[i]>np.mean(amt[i-5:i])*2:
                datev = day['timev'][i]
                fenshi = s.info['min5'][datev]
                closev = fenshi['closev']
                for j in range(1,len(closev)):
                    pre = closev[max(0,j-10):j]
                    if np.std(pre)>np.mean(pre)*0.01:
                        continue
                    if min(closev[j:])<day['closev'][i-1]*(1+rg):
                        continue
                    if np.mean(pre)>day['closev'][i-1]*(1+rg/2):
                        continue
                    day_amt = int(day['closev'][i]*day['volume'][i]/1e7)/10
                    print(f"{code}, {datev}, {fenshi['timev'][j]}, {s.info['name']}, {day_amt}亿")
                    ttt = {'stock':s, 'date':datev, 'time':fenshi['timev'][j], 'name':s.info['name'], 'amount':day_amt}
                    selected[code] = ttt
    a=1