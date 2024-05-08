from core.stock_io_tushare import read_stock_online, read_stocks_online, stock_list, fund_list
from core.tool import *
from core.stock import Stock
import h5py
import os

from enum import Enum
class IOSource(Enum):
    Online = 1
    File = 2

class stock_io:
    ioSource = IOSource.File
    def __init__(self, ioSource):
        self.ioSource = ioSource

    def load_stock(self, stock):
        if stock.loaded:
            return
        sio = stock_io(IOSource.Online)
        stock.clone(sio.read_stock(ts_code=stock.ts_code, start_date=ts2str(stock.start_ts,'%Y%m%d'), end_date=ts2str(stock.end_ts,'%Y%m%d'), freq=stock.freq))

    def read_stock(self, ts_code, asset='E', start_date=None, end_date=None, freq='1min'):
        if start_date == None:
            start_date = '19000101'
        if end_date == None:
            end_date = datetime.date.today().strftime('%Y%m%d')
        if self.ioSource == IOSource.File:
            return self._read_stock_file(ts_code=ts_code, freq=freq)
        if self.ioSource == IOSource.Online:
            if ',' in ts_code:
                return read_stocks_online(ts_code=ts_code, asset=asset, start_date=start_date, end_date=end_date, freq=freq)
            else:
                return read_stock_online(ts_code=ts_code, asset=asset, start_date=start_date, end_date=end_date, freq=freq)

    def _read_stock_file(self, ts_code, freq='1min'):
        if ts_code.startswith('tmp') or ts_code.startswith('cache'):
            str_dir = ts_code
        else:
            str_dir = os.path.join('data', ts_code)
        fn = os.path.join(str_dir, freq+'.h5')
        fn = os.path.abspath(fn)
        stock = Stock()
        if os.path.exists(fn):
            with h5py.File(fn,'r') as f:
                if 'name' in f:
                    stock.name = bytes(f['name']).decode()
                opens = highs = lows = vols = amts = np.zeros(0)
                if 'open' in f:
                    opens = f['open'][:]
                if 'high' in f:
                    highs = f['high'][:]
                if 'low' in f:
                    lows = f['low'][:]
                if 'volume' in f:
                    vols = f['volume'][:]
                if 'amount' in f:
                    amts = f['amount'][:]
                stock.set(ts_code, freq, f['time'][:],
                          opens, f['close'][:],
                          highs, lows,
                          vols, amts)
                if 'k_show' in f:
                    stock.k_show = f['k_show'][:]
        return stock

    def write_stock(self, stock, fn=None):
        if fn is None:
            str_dir = os.path.join('data', stock.ts_code)
            os.makedirs(str_dir,exist_ok=True)
            fn = os.path.join(str_dir, stock.freq+'.h5')
            fn = os.path.abspath(fn)
        else:
            str_dir = fn
            os.makedirs(str_dir,exist_ok=True)
            fn = os.path.join(str_dir,stock.freq+'.h5')
        with h5py.File(fn,'w') as f:
            f['name'] = list(stock.name.encode())
            f['ts_code'] = list(stock.ts_code.encode())
            f['freq'] = stock.freq
            f['time'] = stock.times
            if stock.opens is not None:
                f['open'] = stock.opens
            if stock.closes is not None:
                f['close'] = stock.closes
            if stock.highs is not None:
                f['high'] = stock.highs
            if stock.lows is not None:
                f['low'] = stock.lows
            if stock.volume is not None:
                f['volume'] = stock.volume
            if stock.amount is not None:
                f['amount'] = stock.amount
            try:
                f['k_show'] = stock.k_show
            except Exception as e:
                pass

    def update_stock_file(self, ts_code, asset='E', freq='1min'):
        pass

    def stock_list(self):
        return stock_list()

    def fund_list(self):
        return fund_list()

    def get_stocks_online2file(self):
        pass
