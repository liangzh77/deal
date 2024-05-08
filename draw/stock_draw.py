import numpy as np
import cv2
import ctypes
import time
import math
from PIL import Image, ImageDraw, ImageFont
from core.stock import Stock
from core.tool import float_to_str

class Stock_draw():
    stock = None
    stocks = []
    has_data = False
    from_time = 0
    to_time = 0
    select_time = -1
    move_offset = 0
    draw_in_relative = True
    def __init__(self, stock,from_time,to_time,select_time):
        self._reset()
        self.stock = stock
        self.stocks = []
        self.has_data = True
        self.set_range(from_time,to_time)
        self.select_time = select_time


    def add_stock(self, stock, all_data=False):
        main_ind=-1
        st = Stock()
        st.loaded = True
        st.ts_code = stock.ts_code
        st.name = stock.name
        st.freq = stock.freq
        st.freq_secs = stock.freq_secs
        st.times = np.copy(self.stock.times)
        st.closes = np.zeros(self.stock.length())
        st.k_show = np.zeros(self.stock.length())
        if all_data and stock.opens.shape[0]>0:
            st.opens = np.zeros(self.stock.length())
            st.highs = np.zeros(self.stock.length())
            st.lows = np.zeros(self.stock.length())
            st.volume = np.zeros(self.stock.length())
            st.amount = np.zeros(self.stock.length())
        for i in range(stock.length()):
            t = stock.times[i]
            for oi in range(main_ind+1,self.stock.length()):
                ot = self.stock.times[oi]
                ttt = time.localtime(t)
                if ot==t:# and stock.closes[i]>0:
                    st.k_show[oi] = 1
                    st.closes[oi] = stock.closes[i]
                    if all_data and st.opens.shape[0] > 0:
                        st.opens[oi] = stock.opens[i]
                        st.highs[oi] = stock.highs[i]
                        st.lows[oi] = stock.lows[i]
                        st.volume[oi] = stock.volume[i]
                        st.amount[oi] = stock.amount[i]
                    main_ind+=1
                    break
                if t<ot:
                    break
        self.stocks.append(st)


    def change_freq(self, freq):
        self.stock.change_freq(freq)
        for stock in self.stocks:
            stock.change_freq(freq)
            #stock.k_show=np.zeros(stock.length())
            #stock.k_show[np.where(stock.closes > 0)] = 1


    def set_range(self,from_time,to_time):
        self.from_time = max(self.stock.times[0],from_time)
        self.to_time = min(self.stock.times[-1],to_time)

    def _reset(self):
        self.ret = []
        self.move_offset=0

    def get_data_start_time(self):
        return self.stock.times[0]

    def get_data_to_time(self):
        return self.stock.times[-1]

    def move(self,x):
        from_ind, to_ind, select_ind = self._get_ind_by_time(self.stock)
        from_ind -= x/self.step_x
        to_ind -= x/self.step_x
        from_ind += self.move_offset
        to_ind += self.move_offset
        self.move_offset = from_ind-int(np.floor(from_ind))
        from_ind = int(np.floor(from_ind))
        to_ind = int(np.floor(to_ind))
        if from_ind<0:
            to_ind+=-from_ind
            from_ind=0
        if(to_ind>=self.stock.length()):
            from_ind -= to_ind-self.stock.length()+1
            to_ind = self.stock.length()-1
        self.from_time = self.stock.times[from_ind]
        self.to_time = self.stock.times[to_ind]


    def scale(self,ratio,center):
        h,w = self.m_k.shape[:2]
        center /= w
        center = min(1,center)
        tmp_from_time = self.from_time
        tmp_to_time = self.to_time
        rg = self.to_time-self.from_time
        center_x = self.from_time+rg*center
        rg *= ratio
        self.from_time = center_x-(center_x-self.from_time)/ratio
        self.to_time = center_x+(self.to_time-center_x)/ratio
        if self.from_time<self.get_data_start_time():
            self.from_time = self.get_data_start_time()
        if self.to_time>self.get_data_to_time():
            self.to_time = self.get_data_to_time()
        from_ind, to_ind, select_ind = self._get_ind_by_time(self.stock)
        if from_ind+3>=to_ind:
            self.from_time = tmp_from_time
            self.to_time = tmp_to_time
        return self.from_time, self.to_time


    def move_select_ind(self,off):
        from_ind, to_ind, select_ind = self._get_ind_by_time(self.stock)
        select_ind = select_ind + off
        select_ind = max(from_ind,select_ind)
        select_ind = min(to_ind,select_ind)
        self.select_time = self.stock.times[select_ind]
        return self.stock.times[select_ind]


    def select(self,x):
        from_ind, to_ind, select_ind = self._get_ind_by_time(self.stock)
        size_v = to_ind-from_ind

        off_x = self.step_x/2
        i = (x-off_x)/self.step_x
        i = int(i+0.5)
        i = max(0, i)
        i = min(size_v, i)
        select_ind = i+from_ind
        self.select_time = self.stock.times[select_ind]
        return self.stock.times[select_ind]


    def memsetObject(self,bufferObject):
        "Note, dangerous"
        data = ctypes.POINTER(ctypes.c_char)()
        size = ctypes.c_int()  # Note, int only valid for python 2.5
        ctypes.pythonapi.PyObject_AsCharBuffer(ctypes.py_object(bufferObject), ctypes.pointer(data),
                                               ctypes.pointer(size))
        ctypes.memset(data, 0, size.value)

    def cv2ImgAddText(self, img, text, lefttop, textColor=(0, 255, 0), textSize=20):
        if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        # 创建一个可以在给定图像上绘图的对象
        draw = ImageDraw.Draw(img)
        # 字体的格式
        fontStyle = ImageFont.truetype(
            'draw/STSong.ttf', textSize, encoding='utf-8')
        # 绘制文本
        textColor = (textColor[2],textColor[1],textColor[0])
        draw.text(lefttop, text, textColor, font=fontStyle)
        # 转换回OpenCV格式
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

    def draw(self,m):
        self.memsetObject(m)

        from_time = self.from_time
        from_time = max(from_time, self.stock.times[0])
        to_time = self.to_time
        to_time = min(to_time, self.stock.times[-1])
        if to_time<=from_time:
            from_time = self.stock.times[0]
            to_time = self.stock.times[-1]
        for i in range(len(self.stocks)):
            stock = self.stocks[i]
            from_time = max(from_time, stock.times[0])
            to_time = min(to_time, stock.times[-1])

        if to_time<=from_time:
            return False, False, {}
        self.from_time = from_time
        self.to_time = to_time

        h,w = m.shape[:2]
        nx = int(w * 0.1)
        ny = int(h * 0.01)
        name_len = len(self.stock.name)

        ratio_pos = ratio_neg = min_v = max_v = None
        draw_in_relative = self.draw_in_relative
        if draw_in_relative:
            ratio_pos, ratio_neg = self._get_max_stock_ratio()
        if ratio_pos is None or ratio_neg is None:
            draw_in_relative = False
        if draw_in_relative == False:
            min_v, max_v = self._get_max_stock_abs_val()
        loaded, selected, ret = self.draw_one_stock(m, self.stock, nx, ny, ratio_pos=ratio_pos, ratio_neg=ratio_neg, min_v=min_v, max_v=max_v)

        cl_options = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100), (255, 100, 255),
                      (100, 255, 255), (100, 100, 100)]
        for i in range(len(self.stocks)):
            stock = self.stocks[i]
            clbase = 100
            clrg = 255-clbase
            cl = cl_options[i%len(cl_options)]
            nx2 = nx + (name_len+1)*20
#            m[ny:ny+nh,nx2:nx2+nw,:]=self.cv2ImgAddText(m[ny:ny+nh,nx2:nx2+nw,:],stock.name,(0,0),cl)
            name_len += len(stock.name)+1
            self.draw_one_stock(m, stock, nx2, ny, ratio_pos=ratio_pos, ratio_neg=ratio_neg, min_v=min_v, max_v=max_v, isMainStock=False, cl_stock=cl)
        return loaded, selected, ret

    def _get_max_stock_ratio(self):
        from_ind, to_ind, select_ind = self._get_ind_by_time(self.stock)
        if self.stock.lows.shape[0]==0:
            min_v = np.min(self.stock.closes[from_ind:to_ind + 1])
            max_v = np.max(self.stock.closes[from_ind:to_ind + 1])
            if self.stock.closes[from_ind]==0:
                return None,None
            ratio_pos = max_v/self.stock.closes[from_ind]
            ratio_neg = min_v/self.stock.closes[from_ind]
        else:
            min_v = np.min(self.stock.lows[from_ind:to_ind+1])
            max_v = np.max(self.stock.highs[from_ind:to_ind+1])
            ratio_pos = max_v/self.stock.opens[from_ind]
            ratio_neg = min_v/self.stock.opens[from_ind]
        for stock in self.stocks:
            from_ind, to_ind, select_ind = self._get_ind_by_time(stock)
            closes = stock.closes[np.where(stock.closes[from_ind:to_ind + 1]>0)[0]+from_ind]
            if closes.shape[0]==0:
                continue
            if closes[0]==0:
                return None,None
            min_v = min(closes)
            max_v = max(closes)
            ratio_pos = max(ratio_pos, max_v / closes[0])
            ratio_neg = min(ratio_neg, min_v / closes[0])
        return ratio_pos, ratio_neg

    def _get_max_stock_abs_val(self):
        from_ind, to_ind, select_ind = self._get_ind_by_time(self.stock)
        max_abs = 0
        if self.stock.lows.shape[0]==0:
            min_v = np.min(self.stock.closes[from_ind:to_ind + 1])
            max_v = np.max(self.stock.closes[from_ind:to_ind + 1])
        else:
            min_v = np.min(self.stock.lows[from_ind:to_ind+1])
            max_v = np.max(self.stock.highs[from_ind:to_ind+1])

        for stock in self.stocks:
            from_ind, to_ind, select_ind = self._get_ind_by_time(stock)
            closes = stock.closes[np.where(stock.closes[from_ind:to_ind + 1]>0)[0]+from_ind]
            closes = stock.closes[from_ind:to_ind + 1]
            if closes.shape[0]==0:
                continue
            min_v2 = min(closes)
            max_v2 = max(closes)
            min_v = min(min_v, min_v2)
            max_v = max(max_v, max_v2)
        return min_v, max_v

    def _get_ind_by_time(self, stock):
        from_ind = to_ind = 0
        select_ind = -1
        for i in range(stock.times.shape[0]):
            if self.from_time >= stock.times[i]:
                from_ind = i
            if self.to_time >= stock.times[i]:
                to_ind = i
            if i<stock.times.shape[0]-1 and self.select_time>=stock.times[i] and self.select_time<stock.times[i+1]:
                select_ind = i
            if i==stock.times.shape[0]-1 and self.select_time==stock.times[i]:
                select_ind = i
        return from_ind, to_ind, select_ind

    def draw_info(self,from_ind, to_ind, stock, isMainStock):
        m = self.m_info
        h, w = m.shape[:2]
        # draw start time
        if from_ind>=0 and from_ind<stock.times.shape[0] and isMainStock:
            st = time.localtime(stock.times[from_ind])
            str_val = '{}-{}-{}'.format(st.tm_year, st.tm_mon, st.tm_mday)
            cv2.putText(m,str_val,(int(w * 0.001), h-10), 1, 1,(91, 159, 204))
        # draw end time
        if to_ind>=0 and to_ind<stock.times.shape[0] and isMainStock:
            st = time.localtime(stock.times[to_ind])
            str_val = '{}-{}-{}'.format(st.tm_year,st.tm_mon,st.tm_mday)
            cv2.putText(m,str_val,(int(w-len(str_val)*11), h-10), 1, 1,(91, 159, 204))
        cv2.rectangle(m,(0,0),(w-1,h-1),(91, 159, 204))

    def draw_k(self, stock, from_ind, to_ind, cl_stock, select_ind, isMainStock, ratio_pos=None, ratio_neg=None, min_v=None, max_v=None):
        m = self.m_k
        h, w = m.shape[:2]
        open1 = stock.opens
        close1 = stock.closes
        low = stock.lows
        high = stock.highs
        ma5 = stock.ma5
        ma10 = stock.ma10
        ma20 = stock.ma20
        k_show = stock.k_show

        size_v = to_ind-from_ind+1
        if size_v<2:
            step_x = w
        else:
            step_x = w/size_v
        off_x = step_x/2
        hist_w = min(400,int(step_x/3+0.5))
        self.step_x = step_x

        if stock.opens.shape[0]==0:
            if min_v is None or max_v is None:
                max_v = stock.closes[from_ind]*ratio_pos
                min_v = stock.closes[from_ind]*ratio_neg
        else:
            if min_v is None or max_v is None:
                if isMainStock:
                    max_v = stock.opens[from_ind]*ratio_pos
                    min_v = stock.opens[from_ind]*ratio_neg
                else:
                    max_v = stock.closes[from_ind]*ratio_pos
                    min_v = stock.closes[from_ind]*ratio_neg
        rg_v = max_v-min_v
        scale_v = h/rg_v

        #画K线柱图
        if step_x > 4 and len(self.stocks)==0:
            if stock.opens.shape[0]>0:
                for i in range(size_v):
                    x = int(off_x+i*step_x+0.5)
                    y = int((close1[from_ind+i]-min_v)*scale_v+0.5)
                    y = h-y
                    high_y = int((high[from_ind+i]-min_v)*scale_v+0.5)
                    high_y = h-high_y
                    low_y = int((low[from_ind+i]-min_v) * scale_v + 0.5)
                    low_y = h-low_y
                    open_y = int((open1[from_ind+i]-min_v) * scale_v + 0.5)
                    open_y = h-open_y
                    cl = (0,0,255)
                    if close1[from_ind+i]<open1[from_ind+i]:
                        cl = (0,255,0)
                    #draw hist and high/low
                    m[high_y:low_y+1,x] = cl
                    m[min(open_y,y):max(open_y,y)+1,max(0,x-hist_w):x+hist_w+1] = cl
                    last_x = x
                    last_y = y


        #画K线选择时间点
        if select_ind>=from_ind and select_ind<=to_ind:
            x = int(off_x + (select_ind-from_ind) * step_x + 0.5)
            cv2.rectangle(m,(x-hist_w-1,0),(x+hist_w+1,h),(224,182,64))
            cv2.rectangle(self.m_amt,(x-hist_w-1,0),(x+hist_w+1,self.m_amt.shape[0]),(224,182,64))

        #画K线和ma线
        step_v = 1
        first_i = (size_v-1)%step_v
        is_first = True
        for i in range(first_i,size_v,step_v):
            x = int(off_x+i/step_v*step_x+0.5)
            if from_ind+i<close1.shape[0]:
                if k_show[from_ind+i]==0:
                    continue
                y = int((close1[from_ind+i]-min_v)*scale_v+0.5)
                y = h-y
                ma5_y = int((ma5[from_ind + i]-min_v) * scale_v + 0.5)
                ma5_y = h - ma5_y
                ma10_y = int((ma10[from_ind + i]-min_v) * scale_v + 0.5)
                ma10_y = h - ma10_y
                ma20_y = int((ma20[from_ind + i]-min_v) * scale_v + 0.5)
                ma20_y = h - ma20_y
                if stock.k_show[from_ind+i]==0:
                    continue
                if is_first is False:
                    #draw signal
                    if step_x > 4 and len(self.stocks)==0:
                        if ma5[from_ind + i]>=0 and ma5[from_ind + i-1]>=0:
                            cv2.line(m, (x, ma5_y), (last_x, last_ma5_y), (255, 255, 0))
                        if ma10[from_ind + i] >= 0 and ma10[from_ind + i-1] >= 0:
                            cv2.line(m, (x, ma10_y), (last_x, last_ma10_y), (0, 255, 255))
                        if ma20[from_ind + i] >= 0 and ma20[from_ind + i-1] >= 0:
                            cv2.line(m, (x, ma20_y), (last_x, last_ma20_y), (255, 0, 255))
                        if open1.shape[0]==0:
                            cv2.line(m, (x, y), (last_x, last_y), cl_stock)
                    else:
                        cv2.line(m, (x, y), (last_x, last_y), cl_stock)
                is_first = False
                last_x = x
                last_y = y
                last_ma5_y = ma5_y
                last_ma10_y = ma10_y
                last_ma20_y = ma20_y

        cv2.rectangle(m,(0,0),(w-1,h-1),(91, 159, 204))
        return scale_v, step_x, hist_w

    def draw_k2(self, stock, from_ind, ratio_pos=None, ratio_neg=None, min_v=None, max_v=None):
        m = self.m_k2
        h, w = m.shape[:2]

        if stock.opens.shape[0]==0:
            if min_v is None or max_v is None:
                max_v = stock.closes[from_ind]*ratio_pos
                min_v = stock.closes[from_ind]*ratio_neg
            v0 = stock.closes[from_ind]
        else:
            if min_v is None or max_v is None:
                max_v = stock.opens[from_ind]*ratio_pos
                min_v = stock.opens[from_ind]*ratio_neg
            v0 = stock.opens[from_ind]
        rg_v = max_v-min_v
        scale_v = h/rg_v
        v_y_step = (max_v-min_v)/5
        start_v = v0 - np.floor((v0-min_v)/v_y_step)*v_y_step
        for v_v in np.arange(start_v,max_v+v_y_step/2,v_y_step):
            v_y = int((v_v-min_v) * scale_v + 0.5)
            v_y = min(h-1,h - v_y)
            m[v_y,:] = (128,128,128)
            # draw velue lines, intervals
            v_v_abs = abs(v_v)
            if v_v_abs == 0:
                valid_digits = 1
            else:
                lg = int(math.log10(v_v_abs))
                if v_v == 0:
                    lg = 1
                else:
                    lg = max(0,lg)
                valid_digits = max(5,lg+2)
            if v_v<0:
                valid_digits+=1
            numstr = '{}'.format(v_v)
            if len(numstr)>valid_digits:# and lg>0:
                numstr = numstr[:valid_digits]
            if numstr[-1]=='.':
                numstr = numstr[:-1]
            if self.draw_in_relative or len(self.stocks)==0:
                if v0!=0:
                    cv2.putText(m,'{:.1f}%'.format(v_v/v0*100-100),(5,int(v_y-h*0.004)),1,1,(114,131,229))
            if self.draw_in_relative is False or len(self.stocks)==0:
                cv2.putText(m,numstr,(5,int(v_y-h*0.004)-15),1,1,(224,182,64))

        if False:
            y = int((stock.closes[-1]-min_v) * scale_v + 0.5)
            y = h - y
            if y>=0 and y<h:
                m[y,:] = (178,178,178)
                m[y-int(h*0.022):y,:] = (26,26,26)
                cv2.putText(m,'{}'.format(stock.closes[-1]),(int(w*0.01),int(y-h*0.004)),1,1,(91,159,204))

        cv2.rectangle(m,(0,0),(w-1,h-1),(91, 159, 204))

    def draw_amt(self, stock, from_ind, to_ind, step_x, hist_w):
        m=self.m_amt
        m2=self.m_amt2
        h,w = m.shape[:2]
        amount = stock.amount
        open1 = stock.opens
        close1 = stock.closes
        off_x = step_x/2
        max_amt = np.max(amount[from_ind:to_ind+1])
        max_amt = max(1e-10,max_amt)
        if len(self.stocks)==0:
            size_v = to_ind - from_ind + 1
            max_show = h*0.95
            for i in range(size_v):
                x = int(off_x+i*step_x+0.5)
                cl = (0,0,178)
                if close1[from_ind+i]<open1[from_ind+i]:
                    cl = (0,178,0)
                #draw amount
                m[h-int(amount[from_ind+i]/max_amt*max_show):,x-hist_w:x+hist_w+1] = cl
        cv2.putText(m2,'amount',(5,13),1,1,(178,178,178))
        amt_str = '%.3f'%(max_amt/1e5)
        cv2.putText(m2,amt_str,(5,30),1,1,(178,178,178))

        avg_amount = 0
        if to_ind+1-from_ind>0:
            avg_amount = np.mean(amount[from_ind:to_ind+1])
        cv2.putText(m2,'avg amount',(5,h-40),1,1,(178,178,178))
        amt_str = '%.3f'%(avg_amount/1e5)
        cv2.putText(m2,amt_str,(5,h-23),1,1,(178,178,178))

    def draw_one_stock(self,m, stock, nx, ny, ratio_pos=None, ratio_neg=None, min_v=None, max_v=None, isMainStock=True,cl_stock=(255,255,255)):
        h,w = m.shape[:2]
        area_y1=int(h*0.1)
        area_y2=int(h*0.79)
        area_x1=int(w*0.9)
        self.m_info =  m[0:area_y1,0:area_x1,:]
        self.m_k =     m[area_y1:area_y2,0:area_x1,:]
        self.m_amt =   m[area_y2:h,0:area_x1,:]
        self.m_info2=  m[0:area_y1,area_x1:w,:]
        self.m_k2=     m[area_y1:area_y2,area_x1:w,:]
        self.m_amt2=   m[area_y2:h,area_x1:w,:]

        selected = False
        ret = {}
        if self.has_data == False:
            return stock.loaded, selected, ret

        from_ind, to_ind, select_ind = self._get_ind_by_time(stock)
        open1 = stock.opens
        close1 = stock.closes
        low = stock.lows
        high = stock.highs
        ma5 = stock.ma5
        ma10 = stock.ma10
        ma20 = stock.ma20
        amount = stock.amount

        nw,nh = 300,30
        m[ny:ny+nh,nx:nx+nw,:] = self.cv2ImgAddText(m[ny:ny+nh,nx:nx+nw,:], stock.name, (0,0), cl_stock)
        if select_ind>=from_ind and select_ind<=to_ind and stock.k_show[select_ind]>0:
            s = float_to_str(stock.closes[select_ind],3)
            cv2.putText(m,s,(nx, ny+40), 1, 1.5,cl_stock)

        # draw top info
        self.draw_info(from_ind, to_ind, stock, isMainStock)

        scale_v, step_x, hist_w = self.draw_k(stock, from_ind, to_ind, cl_stock, select_ind, isMainStock, ratio_pos=ratio_pos, ratio_neg=ratio_neg, min_v=min_v, max_v=max_v)
        if isMainStock:
            self.draw_k2(stock,from_ind, ratio_pos=ratio_pos, ratio_neg=ratio_neg, min_v=min_v, max_v=max_v)
        if len(self.stocks)==0 and stock.amount.shape[0]>0:
            self.draw_amt(self.stock, from_ind, to_ind, step_x, hist_w)

        if select_ind>=0 and select_ind<stock.length() and isMainStock:
            #draw details
            ret['close'] = close1[select_ind]
            ret['ma20'] = ma20[select_ind]
            if open1.shape[0]>0:
                ret['open'] = open1[select_ind]
                ret['low'] = low[select_ind]
                ret['high'] = high[select_ind]
            if select_ind==0:
                if open1.shape[0]>0:
                    if open1[select_ind]==0:
                        ret['open_pct'] = 0
                        ret['low_pct'] = 0
                        ret['close_pct'] = 0
                        ret['high_pct'] = 0
                    else:
                        ret['open_pct'] = int((open1[select_ind] / open1[select_ind] - 1) * 1000) / 10
                        ret['low_pct'] = int((low[select_ind] / open1[select_ind] - 1) * 1000) / 10
                        ret['close_pct'] = int((close1[select_ind] / open1[select_ind] - 1) * 1000) / 10
                        ret['high_pct'] = int((high[select_ind] / open1[select_ind] - 1) * 1000) / 10
            else:
                if close1[select_ind-1]==0:
                    ret['close_pct'] = 0
                else:
                    ret['close_pct'] = int((close1[select_ind] / close1[select_ind-1] - 1) * 1000) / 10
                if open1.shape[0]>0:
                    if close1[select_ind-1]==0:
                        ret['open_pct'] = 0
                        ret['low_pct'] = 0
                        ret['high_pct'] = 0
                    else:
                        ret['open_pct'] = int((open1[select_ind] / close1[select_ind - 1] - 1) * 1000) / 10
                        ret['low_pct'] = int((low[select_ind] / close1[select_ind - 1] - 1) * 1000) / 10
                        ret['high_pct'] = int((high[select_ind] / close1[select_ind - 1] - 1) * 1000) / 10
            if ma20[select_ind]==0:
                ret['close_pct_ma20'] = 0
            else:
                ret['close_pct_ma20'] = int((close1[select_ind] / ma20[select_ind] - 1) * 1000) / 10
            if open1.shape[0]>0:
                if ma20[select_ind]==0:
                    ret['open_pct_ma20'] = 0
                    ret['low_pct_ma20'] = 0
                    ret['high_pct_ma20'] = 0
                else:
                    ret['open_pct_ma20'] = int((open1[select_ind] / ma20[select_ind] - 1) * 1000) / 10
                    ret['low_pct_ma20'] = int((low[select_ind] / ma20[select_ind] - 1) * 1000) / 10
                    ret['high_pct_ma20'] = int((high[select_ind] / ma20[select_ind] - 1) * 1000) / 10
                ret['day_amt'] = amount[select_ind] * close1[select_ind]
            ret['time'] = stock.times[select_ind]
            selected = True

        return stock.loaded, selected, ret