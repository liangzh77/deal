import os
from core.stock_io import stock_io, IOSource
from core.stock import Stock
import h5py
from core.tool import load_all_codes, str2ts, ts2str

codes = load_all_codes(['基金'])

sio = stock_io(IOSource.File)
min_month = 36
min_month_ratio = -0.15
min_month_ratio3 = -0.20
min_month_ratio12 = -0.10
stock_ind=0
stocks = {}
cache_dir = 'cache/fund_safe'
os.makedirs(cache_dir,exist_ok=True)

total_fn = cache_dir + '/total.M.h5'
# 读取缓存的total.M.h5
if os.path.exists(total_fn):
    with h5py.File(total_fn, 'r') as f:
        for code in codes.keys():
            stock_ind += 1
#            if stock_ind > 1000:
#                break
            if stock_ind % 1000 == 0:
                print('processed %d / %d' % (stock_ind, len(codes)))
            if code+'.time' not in f:
                continue
            s = Stock()
            s.name = codes[code]['name']
            s.ts_code = code
            s.freq = 'M'
            s.times = f[code+'.time'][:]
            s.closes = f[code+'.close'][:]
            s.loaded = True
            stocks[code] = s
else:
    for code in codes.keys():
        stock_ind+=1
#        if stock_ind>1000:
#            break
        if stock_ind%10==0:
            print('processed %d / %d'%(stock_ind,len(codes)))
        try:
            code_dir = cache_dir + '/' + code
            # 读取缓存的单一stock
            if os.path.exists(code_dir):
                s = sio.read_stock(code_dir, freq='M')
                s.ts_code = code
            else: #读取data文件夹下的stock数据，并写入缓存
                stock = sio.read_stock(code, freq='D')
                stock.change_freq('month')
                s = Stock()
                s.ts_code = stock.ts_code
                s.name = codes[code]['name']
                s.times = stock.times
                s.closes = stock.closes
                s.freq = 'M'
                sio.write_stock(s,code_dir)

            if s.length() <= min_month:
                continue
            stocks[code] = s
        except Exception as e:
            print('cant open file: '+code)
            continue

    # 保存fund_safe合并数据，total.M.h5
    with h5py.File(total_fn, 'w') as f:
        for code,stock in stocks.items():
            f[code+'.time'] = stock.times
            f[code+'.close'] = stock.closes

if 1:
    gain = 1
    win_month = 1
    for start_month in range(str2ts('2000-1','%Y-%m'), str2ts('2022-9','%Y-%m'), 60*60*24*30*win_month):
        total_num = 0
        if start_month>str2ts('2019-1','%Y-%m'):
            a=1
        ret = []
        for code in stocks:
            stock = stocks[code]
            if stock.times[0]>start_month:
                continue
            got = False
            enough_len = True
            start_i=0
            for i in range(stock.length()):
                if stock.times[i]<start_month:
                    start_i=i+1
                    if i+min_month>stock.length():
                        enough_len = False
                        break
                    continue
                if i-start_i==min_month:
                    break
                ratio = stock.closes[i]/stock.closes[i-1]
                if ratio<1+min_month_ratio:
                    got = True
                    break
                if i>=3:
                    ratio = stock.closes[i] / stock.closes[i - 3]
                    if ratio < 1 + min_month_ratio3:
                        got = True
                        break
                if i >= 12:
                    ratio = stock.closes[i] / stock.closes[i - 12]
                    if ratio < 1 + min_month_ratio12:
                        got = True
                        break
            if enough_len:
                total_num+=1
            if got or enough_len==False:
                continue
            param = {}
            param['code'] = code
            param['growth'] = stock.closes[i]/stock.closes[i]
            ret.append(param)

        ret2 = sorted(ret, key=lambda ret:ret['growth'], reverse=True)
        if total_num>0:
            end_month = start_month+60*60*24*365*3
            #print('{},total:{},{}'.format(ts2str(end_month,'%Y-%m'), total_num, ret2))
            stock = stocks[ret2[0]['code']]
            start_i=0
            end_i = stock.length()-1
            for i in range(stock.length()):
                if stock.times[i]<end_month:
                    start_i = i+1
                    continue
                end_i = i
                if stock.times[i]>=end_month+60*60*24*30*win_month:
                    break
            if start_i>=stock.length() or end_i>=stock.length():
                continue
            cur_gain = stock.closes[end_i]/stock.closes[start_i]
            gain *= cur_gain
            start_ts = stock.times[start_i]
            end_ts = stock.times[end_i]
            if ts2str(start_ts,'%Y-%m') == '2019-10':
                a=1
            print('from {} to {}, gain {}, total {}'.format(ts2str(start_ts,'%Y-%m'),ts2str(end_ts,'%Y-%m'),cur_gain, gain))
a=1

#fn = 'tmp/%s_result.txt'%(filter_name)
#os.makedirs('tmp',exist_ok=True)
#with open(fn,'w') as f:
#    for r in ret:
#        f.write(str(r))
#        f.write(str(codes[r['code']])+"\n")


#return [('stock',ret)]