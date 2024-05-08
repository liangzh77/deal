 
#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import requests
import time
import json
import pandas as pd
 
def fenshishuju_dfcf(daima):
 
    if daima[:2] == "sh":
        lsbl = '1.'+daima[2:]
    else:
        lsbl = '0.' + daima[2:]
    wangzhi = "http://push2his.eastmoney.com/api/qt/stock/trends2/get?&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6%2Cf7%2Cf8%2Cf9" \
              "%2Cf10%2Cf11%2Cf12%2Cf13&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58&" \
              "ut=7eea3edcaed734bea9cbfc24409ed989&ndays=1&iscr=0&secid="+lsbl+ \
              "&_=1643253749790"+str(time.time)
    resp = requests.get(wangzhi, timeout=6)
    # print (resp) #打印请求结果的状态码
    data = json.loads(resp.text)
    shuju = {'日期时间': [], '最新价': [], '均价': [], '成交额': []}
    for k in data['data']['trends']:
        lsbl = k.split(",")
        shuju['日期时间'].append(lsbl[0])
        shuju['最新价'].append(lsbl[2])
        shuju['均价'].append(lsbl[-1])
        shuju['成交额'].append(lsbl[-2])
        
    return shuju
 
 
if __name__ == '__main__':
    while 1:
        fenshishuju_dfcf('sh603102')
        time.sleep(3)