import os

filter_name = '最小月季年回撤'

def filter(sio, codes, freq):
    min_month = 36
    growth_name = '三年增长'
    min_month_ratio = -0.15
    min_month_ratio3 = -0.20
    min_month_ratio12 = -0.10
    ret = []
    stock_ind=0
    print(filter_name + ' processing starts')
    for code in codes.keys():
        stock_ind+=1
        if stock_ind%10==0:
            print('processed %d / %d'%(stock_ind,len(codes)))
        try:
            stock = sio.read_stock(code, freq='D')
        except Exception as e:
            print('cant open file: '+code)
            continue
        stock.change_freq('month')
        if stock.length()<=min_month:
            continue
        got = False
        for i in range(stock.length()-min_month,stock.length()):
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
        if got:
            continue
        param = {}
        param['code'] = code
        param[growth_name] = (stock.closes[i]-stock.closes[i-min_month])/stock.closes[i-min_month]
        ret.append(param)

    ret = sorted(ret, key=lambda ret:ret[growth_name], reverse=True)
    fn = 'tmp/%s_result.txt'%(filter_name)
    os.makedirs('tmp',exist_ok=True)
    with open(fn,'w') as f:
        for r in ret:
            f.write(str(r))
            f.write(str(codes[r['code']])+"\n")


    return [('stock',ret)]