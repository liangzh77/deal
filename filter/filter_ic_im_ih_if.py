import os.path

from core.stock_io import stock_io, IOSource
from draw.stock_draw import Stock_draw
from core.tool import *

filter_name = 'IC IM IH IF'

def filter(sio, codes, freq):
    codes = ['399905.SZ','000852.SH','000016.SH','399300.SZ']
    #codes = ['000852.SH','000016.SH']
    fns = []
    names = []
    for code in codes:
        fns.append(code)
        names.append(code)

    return [('overlap',(filter_name, fns, True))]