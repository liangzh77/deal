import sys, os
sys.path.append(os.getcwd())
from mysql_db.mysql_tool import *


#sql = 'select * from zyx.sz000001'
#ret = query_sql(sql, logging=False)

class Chunk:
    def __init__(self):
        self.timev = []
        self.openv = []
        self.closev = []
        self.low = []
        self.high = []
        self.volume = []

    def squeeze(self) -> 'Chunk':
        pass

    def append(self, timev, price, volume):
        self.timev.append(timev)
        self.closev.append(price)
        self.volume.append(volume)

    def append_full(self, time, open, close, low, high, volume):
        pass


class StockInfo:
    start_date=None
    end_date=None
    day=Chunk()
    min5={}


class Stock:
    def __init__(self, code) -> None:
        sql = f'select * from zyx.{code}'
        self.min5 = query_sql(sql, logging=False)
        self.info = self._arange_data()


    def _arange_data(self):
        info = StockInfo()
        for d in self.min5:
            dt, price, volume = d['datetime'], d['price'], d['volume']
            date1, time1 = dt.split(' ')
            if info.start_date is None:
                info.start_date = date1
            info.end_date = date1
            if date1 not in info.min5:
                info.min5[date1] = Chunk()
            info.min5[date1].append(time1, price, volume)
        for min5 in info.min5:
            asdfasdfsadf
        self.info = info
        a=1


    def _calc_daily(self):
        for d in self.min5:
            pass


if __name__ == '__main__':
    stock = Stock('sz000001')
    a=1