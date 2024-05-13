import sys, os
sys.path.append(os.getcwd())
from mysql_db.mysql_tool import *


sql = 'select * from zyx.sz000001'
ret = query_sql(sql, logging=False)
a=1

class stock:
    def __init__(self, code) -> None:
        sql = 'select * from zyx.sz000001'
        self.min5 = query_sql(sql, logging=False)
        self.data = self._arange_data()


    def _arange_data(self):
        data = {'start_date':None,
                'end_date':None,
                'data':{'day':{},
                        'min5':{}}
                }
        for d in self.min5:
            dt, price, volume = d['datetime'], d['price'], d['volume']
            date1, time1 = dt.split(' ')
            if data.start_date is None:
                data.start_date = date1
            data.end_date = date1
            


    def _calc_daily(self):
        for d in self.min5:
            pass
