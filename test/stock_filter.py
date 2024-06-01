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
            fenshi_volume = fenshi['volume']
            for j in range(12,len(closev)):
                pre = closev[max(0,j-12):j-1]
                pre_fenshi_volume = fenshi_volume[max(0,j-12):j-1]
                # 爆量100倍
                if sum(pre_fenshi_volume)*10>fenshi_volume[j]:
                    continue
                # 价提升5点
                if np.mean(pre)*(1+rg/2)>closev[j]:
                    continue
                day_amt = int(day['closev'][i]*volume[i]/1e7)/10
                print(f"{code}, {datev}, {fenshi['timev'][j]}, {s.info['name']}, {day_amt}亿")
                ttt = {'stock':s, 'date':datev, 'time':fenshi['timev'][j], 'name':s.info['name'], 'amount':day_amt}
                selected[code] = ttt
    return selected

# 连续涨停
def filter_stock3(stocks, codes):
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
        for i in range(10,len(amt)-2):
            datev = day['timev'][i]
            fenshi = s.info['min5'][datev]
            if amt[i]<1e8:
                continue
            got_not = False
            # ind0,ind1涨停
            for j in range(2):
                if closev[i+j]<closev[i-1+j]*(1+rg):
                    got_not = True
            if got_not:
                continue
            # ind-1没涨停
            if closev[i-1]>closev[i-2]*(1+rg):
                continue
            # 深套
            if closev[i-10]<closev[i+1]:
                continue
            day_amt = int(day['closev'][i]*day['volume'][i]/1e7)/10
            print(f"{code}, {datev}, {fenshi['timev'][j]}, {s.info['name']}, {day_amt}亿")
            ttt = {'stock':s, 'date':datev, 'time':fenshi['timev'][j], 'name':s.info['name'], 'amount':day_amt}
            selected[code] = ttt
    return selected

def detect_shentao(closev, i, pre_start, pre_end):
    start = max(0,i-pre_start)
    end = max(0,i-pre_end)
    n = 0
    for ind in range(start, end):
        if closev[ind]>closev[i]:
            n+=1
    return n

# 深套，一横一竖涨停
def filter_stock4(stocks, codes):
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
        for i in range(10,len(amt)):
            # 深套
            if detect_shentao(closev, i, 40, 10)<20:
                continue
            # 当天量*2
            if amt[i]<np.mean(amt[i-5:i])*2 and amt[i]<amt[i-1]*2:
                continue
            datev = day['timev'][i]
            fenshi = s.info['min5'][datev]
            fenshi_v = fenshi['closev']
            fenshi_volume = fenshi['volume']
            for j in range(10,len(fenshi_v)):
                pre_fenshi_volume = fenshi_volume[max(0,j-12):j-1]
                # 爆量100倍
#                if sum(pre_fenshi_volume)*1>fenshi_volume[j]:
#                    continue
                pre = fenshi_v[max(0,j-10):j-1]
                # 前面平稳
                if np.std(pre)>np.mean(pre)*0.01:
                    continue
                # 后面封住
                if min(fenshi_v[j:])<day['closev'][i-1]*(1+rg):
                    continue
                # 前面不太低
                if np.mean(pre)>day['closev'][i-1]*(1+rg*0.6) and len(pre)>2:
                    continue
                day_amt = int(day['closev'][i]*volume[i]/1e7)/10
                print(f"{code}, {datev}, {fenshi['timev'][j]}, {s.info['name']}, {day_amt}亿")
                ttt = {'stock':s, 'date':datev, 'time':fenshi['timev'][j], 'name':s.info['name'], 'amount':day_amt}
                selected[code] = ttt
                break
    return selected
