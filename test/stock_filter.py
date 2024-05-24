import numpy as np

# 一横一竖涨停
def filter_stock1(stocks, codes):
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
            # 当天量*2
            if amt[i]<np.mean(amt[i-5:i])*2 and amt[i]<amt[i-1]*2:
                continue
            datev = day['timev'][i]
            fenshi = s.info['min5'][datev]
            closev = fenshi['closev']
            for j in range(10,len(closev)):
                pre = closev[max(0,j-10):j-1]
                # 前面平稳
                if np.std(pre)>np.mean(pre)*0.01:
                    continue
                # 后面封住
                if min(closev[j:])<day['closev'][i-1]*(1+rg):
                    continue
                # 前面不太低
                if np.mean(pre)>day['closev'][i-1]*(1+rg*0.6):# and len(pre)>2:
                    continue
                day_amt = int(day['closev'][i]*day['volume'][i]/1e7)/10
                print(f"{code}, {datev}, {fenshi['timev'][j]}, {s.info['name']}, {day_amt}亿")
                ttt = {'stock':s, 'date':datev, 'time':fenshi['timev'][j], 'name':s.info['name'], 'amount':day_amt}
                selected[code] = ttt
                break
    return selected

# 爆量涨停
def filter_stock2(stocks, codes):
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
            datev = day['timev'][i]
            fenshi = s.info['min5'][datev]
            closev = fenshi['closev']
            volume = fenshi['volume']
            for j in range(12,len(closev)):
                pre = closev[max(0,j-12):j-1]
                pre_volume = volume[max(0,j-12):j-1]
                # 爆量100倍
                if sum(pre_volume)*10>volume[j]:
                    continue
                # 价提升5点
                if np.mean(pre)*(1+rg/2)>closev[j]:
                    continue
                # # 前面平稳
                # if np.std(pre)>np.mean(pre)*0.01:
                #     continue
                # # 后面封住
                # if min(closev[j:])<day['closev'][i-1]*(1+rg):
                #     continue
                # # 前面不太低
                # if np.mean(pre)>day['closev'][i-1]*(1+rg*0.6):
                #     continue
                day_amt = int(day['closev'][i]*day['volume'][i]/1e7)/10
                print(f"{code}, {datev}, {fenshi['timev'][j]}, {s.info['name']}, {day_amt}亿")
                ttt = {'stock':s, 'date':datev, 'time':fenshi['timev'][j], 'name':s.info['name'], 'amount':day_amt}
                selected[code] = ttt
    return selected