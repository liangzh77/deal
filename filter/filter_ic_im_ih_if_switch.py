import os.path

from core.stock_io import stock_io, IOSource
from draw.stock_draw import Stock_draw
from core.tool import *

filter_name = 'IC IM IH IF 切换'

def clear_all_but_closes(s):
    s.opens=np.zeros(0)
    s.highs=np.zeros(0)
    s.lows=np.zeros(0)
    s.volume=np.zeros(0)
    s.amount=np.zeros(0)

def find_low(ss,ind):
    low=1e10
    name = ''
    for n in ss:
        s2 = ss[n]
        if s2.closes[ind]<low:
            low = s2.closes[ind]
            name = n
    return low, name

def filter(sio, codes, freq):
    baseline_win = 200
    low_thresh = -10

    codes = {'ic':'399905.SZ','im':'000852.SH','ih':'000016.SH','if':'399300.SZ'}
    code_names = {'399905.SZ':'中证500','000852.SH':'中证1000','000016.SH':'上证50','399300.SZ':'沪深300'}
#    codes = {'ic':'399905.SZ','ih':'000016.SH'}
    multiplier = {'ic':200,'im':200,'ih':300,'if':300}
    sio = stock_io(IOSource.File)
    sd = None

    stocks = {}
    stocks2 = {}
    for name in codes:
        code = codes[name]
        stock = sio.read_stock(code, freq='D')
        clear_all_but_closes(stock)
        if sd is None:
            sd = Stock_draw(stock, 0, 0, -1)
            is_main_stock = True
        else:
            sd.add_stock(stock)
            stock = sd.stocks[len(sd.stocks)-1]
            is_main_stock = False
        stocks[name] = stock.clone()
        stock.closes *= multiplier[name]/10000
        remove_baseline(stock,baseline_win)
        stocks2[name] = stock

    num = len(sd.stocks)+1
    for i in range(sd.stock.length()):
        mean_val = sd.stock.closes[i]
        for s in sd.stocks:
            mean_val += s.closes[i]
        mean_val /= num
        sd.stock.closes[i] -= mean_val
        for s in sd.stocks:
            s.closes[i] -= mean_val

    results = []
    closesGain = np.zeros(sd.stock.length())
    closesBase = np.zeros(sd.stock.length())
    gain2 = 200000
    base2 = 200000
    closesGain[0] = gain2
    closesBase[0] = base2
    cur_name = ''
    buy_short = False
    buy_short_start_gain = 0
    idling = False
    idle_start_ind = 0
    status=''
    for i in range(s.length()-1):
        low, name = find_low(stocks2, i)
        time_struct = time.localtime(stocks2[name].times[i])
        time_str = time.strftime("%Y-%m-%d", time_struct)
        if name != cur_name and low < low_thresh:
            cur_name = name
            if status!='long '+cur_name:
                print(time_str+',long '+cur_name)
            status = 'long '+cur_name
        if cur_name != '' and idling is False:
            if cur_name=='ic' or cur_name=='im':
                gain2 += (stocks[cur_name].closes[i + 1] - stocks[cur_name].closes[i]) * multiplier[cur_name]
                buy_short = False
                if status != 'long ' + cur_name:
                    print(time_str+',long ' + cur_name)
                status = 'long ' + cur_name
            else:
                if low < -7 and cur_name!='ic' and cur_name!='im':
                    if buy_short is False:
                        buy_short = True
                        buy_short_start_gain = gain2
                        if status != 'short':
                            print(time_str+',short')
                        status = 'short'
                    gain2 -= (stocks['ic'].closes[i + 1] - stocks['ic'].closes[i]) * multiplier['ic']
                    if gain2 < buy_short_start_gain - 200000:
                        idling = True
                        idle_start_ind = i
                        print('{},start idling'.format(time_str))
                else:
                    gain2 += (stocks['ic'].closes[i + 1] - stocks['ic'].closes[i]) * multiplier['ic']
                    if status != 'long 2 ic':
                        print(time_str+',long 2 ic')
                    status = 'long 2 ic'
        if idling:
            if i > idle_start_ind + 22:
                buy_short = False
                idling = False
                print('{},stop idling'.format(time_str))

        closesGain[i+1] = gain2
        day_gain=0
        for tts in stocks:
            day_gain += (stocks[tts].closes[i+1]-stocks[tts].closes[i])*multiplier[tts]
        base2 += day_gain/len(codes)
        closesBase[i+1] = base2
    stock = Stock()
    stock.set('gain','D',s.times,None,closesGain,None,None,None,None)
    gain_fn = 'tmp/'+str(time.time())
    stock.name='我的收益曲线'
    sio.write_stock(stock,gain_fn)

    stock.set('gain','D',s.times,None,closesBase,None,None,None,None)
    base_fn = 'tmp/'+str(time.time())
    stock.name='基础收益曲线'
    sio.write_stock(stock,base_fn)

    fns = [gain_fn,base_fn]
    results.append(('overlap',('收益曲线', fns, False)))

    sd.stock.name = code_names[sd.stock.ts_code]
    fn = 'tmp/'+str(time.time())
    fns = [fn]
    sio.write_stock(sd.stock,fn)
    for s in sd.stocks:
        s.name = code_names[s.ts_code]
        fn = 'tmp/'+str(time.time())
        fns.append(fn)
        sio.write_stock(s, fn)

    results.append(('overlap',(filter_name, fns, False)))
    return results