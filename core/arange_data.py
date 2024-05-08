from core.stock_io import stock_io, IOSource
from core.tool import *
import os

sio = stock_io(IOSource.Online)

if 1:
    from core.stock_io_csv import *

    for root, dirs, files in os.walk('../orig_data/csv数据'):
        for name in files:
            fn = os.path.join(root, name)
            if(fn.find('主力连续')<0):
                continue
            stock = read_stock_csv(fn)
            sio.write_stock(stock)
