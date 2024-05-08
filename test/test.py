from core.stock_io import stock_io, IOSource
from core.tool import *
import os
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np

if 0:
    #修改基金文件
    sio = stock_io(IOSource.File)
    fn = 'settings/基金.txt'
    with open(fn, 'r', encoding='utf-8') as f:
        ls = f.readlines()
    for i in range(1, len(ls)):
        line = ls[i]
        strs = line.split(',')
        code = strs[0]
        if os.path.exists('data/'+code) is False:
            continue
        try:
            if code == '005841.OF':
                a=1
            stock = sio.read_stock(ts_code=code, asset='I', freq='D')
        except Exception as r:
            print('%s'%(r))
        if stock is None or stock.length()==0:
            continue
        if stock.opens is None:
            continue
        stock.opens = stock.highs = stock.lows = stock.volume = stock.amount = None
        sio.write_stock(stock)
        print('saved '+code)

if 0:
    with open('settings/期货.txt','r',encoding='utf-8') as f:
        lines = f.readlines()
        for i in range(1,len(lines)):
            l = lines[i]
            if len(l)>0 and l[-1]=='\n':
                l=l[:-1]
            s = l.split(',')
            if s[0].find('次')>=0:
                s[1]+='次'
            else:
                s[1]+='主'
            lines[i] = s[0]+','+s[1]+'\n'

    with open('settings/期货2.txt','w',encoding='utf-8') as f:
        f.writelines(lines)


if 0:
    def cv2ImgAddText(img, text, lefttop, textColor=(0, 255, 0), textSize=20):
        if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        # 创建一个可以在给定图像上绘图的对象
        draw = ImageDraw.Draw(img)
        # 字体的格式
        fontStyle = ImageFont.truetype(
            'D:/liangz77/python_projects/deal/draw/STSong.ttf', textSize, encoding='utf-8')
        # 绘制文本
        draw.text(lefttop, text, textColor, font=fontStyle)
        # 转换回OpenCV格式
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

    m = np.zeros((500,500,3),dtype=np.uint8)
    m = cv2ImgAddText(m,'啊好肥哦是vNSA',(250,250))
    cv2.imshow('',m)
    cv2.waitKey()

if 0:
    sio = stock_io(IOSource.Online)
    stock = sio.read_stock(ts_code='000001.sz', freq='D')

if 0:
    ls = sio.stock_list()

    a=1

if 0:
    stock = sio.read_stock(ts_code='000001.sz', asset='E', start_date='20180101', end_date='20181011', freq='D')
    print(stock.length())
    print(ts2str(stock.times[0], '%Y-%m-%d %H:%M:%S'))
    print(ts2str(stock.times[-1], '%Y-%m-%d %H:%M:%S'))
    print(stock.opens[0],stock.closes[0],stock.highs[0],stock.lows[0])
    sio.write_stock(stock)