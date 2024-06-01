
# 第二天open买，第三天close卖
def eval1(sels):
    gain = 1
    for code in sels:
        sel = sels[code]
        stock = sel['stock']
        day = stock.info['day']
        day_ind = day['timev'].index(sel['date'])
        if sel['amount']<5:
            continue
        if day_ind+2<len(day['timev']):
            ttt = day['closev'][day_ind+2]/day['openv'][day_ind+1]
            gain *= ttt
            print("{:.2f}".format(gain),sel['amount'],"{:.2f}".format(ttt))

# 第二天open买，中午没涨停就卖
def eval2(sels):
    gain = 1
    for code in sels:
        # 涨停幅度
        if code[2:4] in ['30','68']:
            rg = 0.199
        else:
            rg = 0.099
        sel = sels[code]
        stock = sel['stock']
        day = stock.info['day']
        day_ind = day['timev'].index(sel['date'])
        # 量大于一亿
        if sel['amount']<1:
            continue
        if day_ind+2<len(day['timev']):
            # 第二天不涨停就买
            buy_v = day['openv'][day_ind+1]
            if buy_v>day['closev'][day_ind]*(1+rg):
                continue
            sell_v = day['closev'][-1]
            for i in range(day_ind+2,len(day['timev'])):
                min5=stock.info['min5'][day['timev'][i]]
                # 第三天11:30没涨停就卖
                if min5['closev'][23]<day['closev'][i-1]*(1+rg):
                    sell_v = min5['closev'][23]
                    break

            ttt = sell_v/buy_v
            gain *= ttt
            print('cash:'+"{:.2f}".format(gain),stock.info['name'],sel['date'],sel['time'],f"{sel['amount']}亿",'gain:'+"{:.2f}".format(ttt))
            