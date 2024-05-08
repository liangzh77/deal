import cv2
import numpy as np
from core.stock_io import stock_io, IOSource
from draw.stock_draw import Stock_draw
from tkinter import Tk,StringVar,DoubleVar,Entry,W,Radiobutton,Listbox,Button
from tkinter.ttk import Combobox,Label
from PIL import Image, ImageTk
import os
import time
import math
from filter import filter_list
from core.tool import float_to_str, load_all_codes
import shutil

class Draw_ui:
    def __init__(self):
        self._reset()

        root = Tk()
        self.root = root
        root.state('zoomed')
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        desc_width = 300
        view_width = width-desc_width
        view_height = int(height*0.95)
        info_width = desc_width
        info_height = 1
        font = 13
        self.m = np.zeros((view_height, view_width, 3),dtype=np.ubyte)
#        root.geometry(str(view_width + info_width) + 'x' + str(view_height))
#        root.resizable(width=False, height=False)

        # 图形区
        self.main_view = Label(root)
        self.main_view.place(x=info_width + 1, y=0, width=view_width, height=view_height)
        self.root.bind('<Key>', self.on_key_img)
        self.main_view.bind('<Button>', self.on_mouse_press_img)
        self.main_view.bind('<Motion>', self.on_mouse_motion_img)
        self.main_view.bind("<MouseWheel>", self.on_mouse_wheel_img)

        # 时间
        frame, info_height = self._init_info_frame(root, info_width, info_height, 47)
        self.var_time = StringVar()
        label = Label(frame, font=('', font), textvariable=self.var_time).grid(row=0, column=0)
        self.var_desc = StringVar()
        label = Label(frame, font=('', font), textvariable=self.var_desc).grid(row=1, column=0)

        # stock 信息
        frame, info_height = self._init_info_frame(root, info_width, info_height, 130)
        label = Label(frame, font=('', font), text='  价  ').grid(row=0, column=1)
        label = Label(frame, font=('', font), text='  当日% ').grid(row=0, column=2)
        label = Label(frame, font=('', font), text='  /MA20  ').grid(row=0, column=3)
        label = Label(frame, font=('', font), text='开').grid(row=1, column=0, sticky=W)
        self.var_open_price = DoubleVar()
        self.label_open_price = Label(frame, font=('', font), textvariable=self.var_open_price)
        self.label_open_price.grid(row=1, column=1, sticky=W)
        self.var_open_pct = DoubleVar()
        self.label_open_pct = Label(frame, font=('', font), textvariable=self.var_open_pct)
        self.label_open_pct.grid(row=1, column=2)
        self.var_open_pct_ma20 = DoubleVar()
        self.label_open_pct_ma20 = Label(frame, font=('', font), textvariable=self.var_open_pct_ma20)
        self.label_open_pct_ma20.grid(row=1, column=3)
        label = Label(frame, font=('', font), text='低').grid(row=2, column=0, sticky=W)
        self.var_low_price = DoubleVar()
        self.label_low_price = Label(frame, font=('', font), textvariable=self.var_low_price)
        self.label_low_price.grid(row=2, column=1, sticky=W)
        self.var_low_pct = DoubleVar()
        self.label_low_pct = Label(frame, font=('', font), textvariable=self.var_low_pct)
        self.label_low_pct.grid(row=2, column=2)
        self.var_low_pct_ma20 = DoubleVar()
        self.label_low_pct_ma20 = Label(frame, font=('', font), textvariable=self.var_low_pct_ma20)
        self.label_low_pct_ma20.grid(row=2, column=3)
        label = Label(frame, font=('', font), text='高').grid(row=3, column=0, sticky=W)
        self.var_high_price = DoubleVar()
        self.label_high_price = Label(frame, font=('', font), textvariable=self.var_high_price)
        self.label_high_price.grid(row=3, column=1, sticky=W)
        self.var_high_pct = DoubleVar()
        self.label_high_pct = Label(frame, font=('', font), textvariable=self.var_high_pct)
        self.label_high_pct.grid(row=3, column=2)
        self.var_high_pct_ma20 = DoubleVar()
        self.label_high_pct_ma20 = Label(frame, font=('', font), textvariable=self.var_high_pct_ma20)
        self.label_high_pct_ma20.grid(row=3, column=3)
        label = Label(frame, font=('', font), text='收').grid(row=4, column=0, sticky=W)
        self.var_close_price = DoubleVar()
        self.label_close_price = Label(frame, font=('', font), textvariable=self.var_close_price)
        self.label_close_price.grid(row=4, column=1, sticky=W)
        self.var_close_pct = DoubleVar()
        self.label_close_pct = Label(frame, font=('', font), textvariable=self.var_close_pct)
        self.label_close_pct.grid(row=4, column=2)
        self.var_close_pct_ma20 = DoubleVar()
        self.label_close_pct_ma20 = Label(frame, font=('', font), textvariable=self.var_close_pct_ma20)
        self.label_close_pct_ma20.grid(row=4, column=3)
        label = Label(frame, font=('', font), text='MA20').grid(row=5, column=0, sticky=W)
        self.var_ma20_price = DoubleVar()
        self.label_ma20_price = Label(frame, font=('', font), textvariable=self.var_ma20_price)
        self.label_ma20_price.grid(row=5, column=1, sticky=W)

        # 选择stock
        frame, info_height = self._init_info_frame(root, info_width, info_height, 94)
        label = Label(frame, font=('', font), text='数据源').grid(row=0, column=0, sticky=W)
        self.combo_source = Combobox(frame, font=('', font), state='readonly', values=[''])
        self.combo_source.bind('<<ComboboxSelected>>', self._cbSelectSource)
        self.combo_source.grid(row=0, column=1)
        self.combo_source.current(0)
        label = Label(frame, font=('', font), text='行  业').grid(row=1, column=0, sticky=W)
        self.combo_industry = Combobox(frame, font=('', font), state='readonly', values=['全行业'])
        self.combo_industry.bind('<<ComboboxSelected>>', self._cbSelectIndustry)
        self.combo_industry.grid(row=1, column=1)
        self.combo_industry.current(0)
        label = Label(frame, font=('', font), text='区  域').grid(row=2, column=0, sticky=W)
        self.combo_area = Combobox(frame, font=('', font), state='readonly', values=['全区域'])
        self.combo_area.bind('<<ComboboxSelected>>', self._cbSelectArea)
        self.combo_area.grid(row=2, column=1)
        self.combo_area.current(0)
        label = Label(frame, font=('', font), text='关键字').grid(row=3, column=0, sticky=W)
        self.keyword_text = Entry(frame)
        self.keyword_text.bind('<KeyRelease>', self._cbKeywordText)
        self.keyword_text.grid(row=3, column=1)

        # 周期选择
        self.period = StringVar()
        self.period.set('day')
        frame, info_height = self._init_info_frame(root, info_width, info_height, 30)
        Radiobutton(frame, text='日K',value='day',variable=self.period,font=('',font),command=self._cbSelectPeriod).grid(row=0,column=0)
        Radiobutton(frame, text='周K',value='week',variable=self.period,font=('',font),command=self._cbSelectPeriod).grid(row=0,column=1)
        Radiobutton(frame, text='月K',value='month',variable=self.period,font=('',font),command=self._cbSelectPeriod).grid(row=0,column=2)
        Radiobutton(frame, text='季K',value='season',variable=self.period,font=('',font),command=self._cbSelectPeriod).grid(row=0,column=3)
        Radiobutton(frame, text='年K',value='year',variable=self.period,font=('',font),command=self._cbSelectPeriod).grid(row=0,column=4)

        # 股票列表
        frame, info_height = self._init_info_frame(root, info_width, info_height, 200)
        self.list_stock = Listbox(frame, font=('', font), width=31, height=11)
        self.list_stock.bind('<<ListboxSelect>>', self._cbSelectStock)
        self.list_stock.grid(row=0, column=0)

        # 片段操作
        frame, info_height = self._init_info_frame(root, info_width, info_height, 32)
        Button(frame, text='添加',width=8,command=self._cbSegmentAdd).grid(row=0,column=0)
        Button(frame, text='叠加',width=8,command=self._cbSegmentOverlap).grid(row=0,column=1)
        Button(frame, text='删除',width=8,command=self._cbSegmentDel).grid(row=0,column=2)
        Button(frame, text='清空',width=8,command=self._cbSegmentClear).grid(row=0,column=3)

        # 片段列表
        frame, info_height = self._init_info_frame(root, info_width, info_height, 200)
        self.list_segment = Listbox(frame, font=('', font), width=31, height=11)
        self.list_segment.bind('<<ListboxSelect>>', self._cbSelectSegment)
        self.list_segment.grid(row=0, column=0)
        self.segment_cache={}

        # 过滤器
        frame, info_height = self._init_info_frame(root, info_width, info_height, 200)
        self.list_filter = Listbox(frame, font=('', font), width=31, height=11)
        self.list_filter.bind('<<ListboxSelect>>', self._cbSelectFilter)
        self.list_filter.grid(row=0, column=0)
        flist = filter_list.get_filter_list()
        for f in flist.keys():
            self.list_filter.insert('end', f)

        self._load_setting()
        self._change_data_source()
        self.sio = stock_io(IOSource.File)
#        self._load_stock()
#        self._draw_stock()
        root.mainloop()

    def _cbSelectPeriod(self):
        if len(self.sd.stocks)==0:
            self._load_stock()
        else:
            self._load_segment()
        self._draw_stock()

    def _cbKeywordText(self, w):
        self._keyword_stocks()

    def _init_info_frame(self, root, info_width, info_height, height):
        frame2 = Label(root,relief='groove')
        frame2.place(x=1,y=info_height,width=info_width, height=height)
        frame = Label(frame2)
        frame.place(x=1,y=1,width=info_width-2, height=height-2)
        info_height += height
        return frame, info_height

    def on_key_img(self,event):
        key = event.keysym.lower()
        if key == 'left':
            self.select_time = self.sd.move_select_ind(-1)
            self._draw_stock()
        elif key == 'right':
            self.select_time = self.sd.move_select_ind(1)
            self._draw_stock()

    def on_mouse_press_img(self, event):
        if self.sd is None:
            return
        self.start_x = event.x
        self.start_y = event.y
        if event.num==3:
            self.select_time = self.sd.select(event.x)
        self._draw_stock()

    def _state_str(self,state):
        mods = ('Shift', 'Lock', 'Control',
                'Mod1', 'Mod2', 'Mod3', 'Mod4', 'Mod5',
                'Button1', 'Button2', 'Button3', 'Button4', 'Button5')
        s = []
        for i, n in enumerate(mods):
            if state & (1 << i):
                s.append(n)
        return s

    def on_mouse_motion_img(self, event):
        if self.sd is None:
            return
        if 'Button1' in self._state_str(event.state):
            dx = event.x - self.start_x
            if dx != 0:
                self._move(dx)
                self.start_x = event.x
                self.start_y = event.y
            self.from_time, self.to_time = self.sd.from_time, self.sd.to_time
        if 'Button3' in self._state_str(event.state):
            self.start_x = event.x
            self.start_y = event.y
            self.select_time = self.sd.select(event.x)
            self._draw_stock()

    def on_mouse_wheel_img(self, event):
        self.from_time, self.to_time = self.sd.scale(1 + event.delta/500, event.x)
#        self.from_time = self.sd.stock.times[int(self.sd.draw_start)]
#        self.to_time = self.sd.stock.times[min(int(self.sd.draw_end),self.sd.stock.length()-1)]
        self._draw_stock()

    def _move(self,x):
        self.sd.move(x)
        self._draw_stock()

    def _photo_image(self, image: np.ndarray):
        height, width = image.shape[:2]
        ppm_header = f'P6 {width} {height} 255 '.encode()
        data = ppm_header + cv2.cvtColor(image, cv2.COLOR_BGR2RGB).tobytes()
        return ImageTk.PhotoImage(width=width, height=height, data=data, format='PPM')

    def _cbSelectIndustry(self, event):
        self._keyword_stocks()
        self._load_stock()
        self._draw_stock()

    def _cbSelectArea(self, event):
        self._keyword_stocks()
        self._load_stock()
        self._draw_stock()

    def _cbSegmentAdd(self):
        param = {}
        param['stocks'] = [self.current_stock_code]
        name = str(time.time())
        self.segments[name] = param
        self.list_segment.insert('end', name)
        self.current_segment_name = name

        self._load_segment()
        self._draw_stock()

    def _cbSegmentOverlap(self):
        if self.current_segment_name in self.segments:
            if self.current_stock_code not in self.segments[self.current_segment_name]['stocks']:
                self.segments[self.current_segment_name]['stocks'].append(self.current_stock_code)
            for i in range(self.list_segment.size()):
                if self.list_segment.get(i)==self.current_segment_name:
                    self.list_segment.select_set(i)

            self._load_segment()
            self._draw_stock()

    def _load_segment(self):
        sels = self.list_segment.curselection()
        if len(sels)==0:
            return
        name = self.list_segment.get(sels[0])
        self.current_segment_name = name
        if name in self.segment_cache:
            from_time = self.sd.from_time
            to_time = self.sd.to_time
            select_time = self.sd.select_time
            self.sd = self.segment_cache[name]['sd']
            self.sd.from_time = from_time
            self.sd.to_time = to_time
            self.sd.select_time = select_time
            return
        first = True
        for stock_code in self.segments[name]['stocks']:
            stock = self.sio.read_stock(stock_code, freq=self.freq)
            if stock_code in self.all_codes:
                stock.name = self.all_codes[stock_code]['name']
            if first:
                first = False
                self.sd = Stock_draw(stock, self.from_time, self.to_time, self.select_time)
            else:
                if 'aligned' in self.segments[name]:
                    self.sd.stocks.append(stock)
                else:
                    self.sd.add_stock(stock)
        if 'draw_in_relative' in self.segments[name]:
            self.sd.draw_in_relative = self.segments[name]['draw_in_relative']
        period = self.period.get()
        self.sd.change_freq(period)
        if 'mark time' in self.segments[name]:
            self.sd.from_time = self.segments[name]['mark time']['from_time']
            self.sd.to_time = self.segments[name]['mark time']['to_time']

        param = {}
        param['time'] = time.time()
        param['sd'] = self.sd
        self.segment_cache[name] = param
        if len(self.segment_cache)>3:
            old_name=''
            old_time=time.time()
            for n in self.segment_cache:
                if self.segment_cache[n]['time']<old_time:
                    old_name = n
                    old_time = self.segment_cache[n]['time']
            self.segment_cache.pop(old_name)

    def _cbSegmentDel(self):
        for i in range(self.list_segment.size()):
            if self.list_segment.get(i) == self.current_segment_name:
                self.list_segment.delete(i)
                self.current_segment_name = ''
                break

    def _cbSegmentClear(self):
        self.list_segment.delete(0,self.list_segment.size())
        self.current_segment_name = ''

    def _cbSelectSegment(self, event):
        self._load_segment()
        self._draw_stock()

    def _cbSelectFilter(self, event):
        flist = filter_list.get_filter_list()
        sels = self.list_filter.curselection()
        if len(sels)==0:
            return
        code_list = list(self.list_stock.get(0, 'end'))
        code_map = {}
        for list_ind in range(len(code_list)):
            p = code_list[list_ind].find(' ')
            if p<0:
                continue
            code = code_list[list_ind][:p]
            if code in self.stock_codes:
                code_map[code] = self.stock_codes[code]
        rets = list(flist.values())[sels[0]](self.sio,code_map,'')
        for ret in rets:
            type, res = ret
            if type=='stock':
                for code in res:
                    param = {}
                    param['stocks'] = [code['code']]
                    self.segments[code['name']] = param
                    self.list_segment.insert('end', code['name'])

            if type=='overlap':
                seg_name, fns, draw_in_relative = res
#                for i in range(len(fns)):
#                    self.all_codes[fns[i]] = {'name':self.all_codes[codes[i]]['name']}
                param = {}
                param['stocks'] = []
                for fn in fns:
                    param['stocks'].append(fn)
                param['aligned'] = True
                param['draw_in_relative'] = draw_in_relative
                name = list(flist.keys())[sels[0]]
                if name not in self.segments:
                    self.segments[seg_name] = param
                    self.list_segment.insert('end', seg_name)
                self.current_segment_name = seg_name
                sel_ind=-1
                for i in range(self.list_segment.size()):
                    if seg_name == self.list_segment.get(i):
                        sel_ind=i
        if sel_ind>=0:
            self.list_segment.select_set(sel_ind)
            self._load_segment()
            self._draw_stock()

    def _cbSelectStock(self, event):
        sels = self.list_stock.curselection()#.split(' ')[0]
        if len(sels)==0:
            return
        self.current_stock_code = self.list_stock.get(sels[0]).split(' ')[0]
        self._load_stock()
        self._draw_stock()

    def _cbSelectSource(self, event):
        self._change_data_source()
#        self._load_stock()
#        self._draw_stock()

    def _draw_stock(self):
        stock_loaded, selected, ret = self.sd.draw(self.m)

        time_str = ''
        if selected:
            self.var_low_price.set('')
            self.var_high_price.set('')
            self.var_open_price.set('')
            if 'low' in ret:
                self.var_low_price.set(float_to_str(ret['low'], 3))
            if 'high' in ret:
                self.var_high_price.set(float_to_str(ret['high'], 3))
            if 'open' in ret:
                self.var_open_price.set(float_to_str(ret['open'], 3))
            self.var_close_price.set(float_to_str(ret['close'], 3))
            self.var_ma20_price.set(float_to_str(ret['ma20'], 3))
            if 'close_pct' in ret:
                if ret['close_pct'] < 0:
                    self.label_close_pct["foreground"] = 'green'
                else:
                    self.label_close_pct["foreground"] = 'red'

            if 'close_pct_ma20' in ret:
                if ret['close_pct_ma20'] < 0:
                    self.label_close_pct_ma20["foreground"] = 'green'
                else:
                    self.label_close_pct_ma20["foreground"] = 'red'

            if 'high_pct' in ret:
                if ret['high_pct'] < 0:
                    self.label_high_pct["foreground"] = 'green'
                else:
                    self.label_high_pct["foreground"] = 'red'

            if 'high_pct_ma20' in ret:
                if ret['high_pct_ma20'] < 0:
                    self.label_high_pct_ma20["foreground"] = 'green'
                else:
                    self.label_high_pct_ma20["foreground"] = 'red'

            self.var_open_pct.set('')
            self.var_low_pct.set('')
            self.var_close_pct.set('')
            self.var_high_pct.set('')
            self.var_open_pct_ma20.set('')
            self.var_low_pct_ma20.set('')
            self.var_close_pct_ma20.set('')
            self.var_high_pct_ma20.set('')

            if 'open_pct' in ret:
                self.var_open_pct.set(str(ret['open_pct']) + '%')
            if 'low_pct' in ret:
                self.var_low_pct.set(str(ret['low_pct']) + '%')
            self.var_close_pct.set(str(ret['close_pct']) + '%')
            if 'high_pct' in ret:
                self.var_high_pct.set(str(ret['high_pct']) + '%')
            if 'open_pct_ma20' in ret:
                self.var_open_pct_ma20.set(str(ret['open_pct_ma20']) + '%')
            if 'low_pct_ma20' in ret:
                self.var_low_pct_ma20.set(str(ret['low_pct_ma20']) + '%')
            self.var_close_pct_ma20.set(str(ret['close_pct_ma20']) + '%')
            if 'high_pct_ma20' in ret:
                self.var_high_pct_ma20.set(str(ret['high_pct_ma20']) + '%')
#            self.var_day_amt.set(float_to_str(ret['day_amt'], 2))
            time_sec = ret['time']
            time_struct = time.localtime(time_sec)
            time_str = time.strftime("%Y-%m-%d %H:%M", time_struct)
        self.var_time.set(self.sd.stock.ts_code + ' ' + time_str)
        s = ''
        if self.sd.stock.ts_code in self.all_codes:
            if 'name' in self.stock_keys:
                s += self.all_codes[self.sd.stock.ts_code]['name']
            if 'area' in self.stock_keys:
                if 'area' in self.all_codes[self.sd.stock.ts_code]:
                    s += ' 区域[' + self.all_codes[self.sd.stock.ts_code]['area']+']'
            if 'industry' in self.stock_keys:
                if 'industry' in self.all_codes[self.sd.stock.ts_code]:
                    s += ' 行业[' + self.all_codes[self.sd.stock.ts_code]['industry']+']'
        self.var_desc.set(s)

        img = self._photo_image(self.m)
        self.main_view['image'] = img
        self.main_view.image = img

    def _change_data_source(self):
        self.current_data_source = self.combo_source.get()
        self.stock_area = {}
        self.stock_industry = {}
        self.stock_codes = {}
        if self.current_data_source=='全部':
            for source in self.data_sources:
                self.load_data_source(source)
        else:
            self.load_data_source(self.current_data_source)
        area_list = list(self.stock_area.keys())
        area_list.insert(0, '全区域')
        self.combo_area['values'] = area_list
        self.combo_area.current(0)
        industry_list = list(self.stock_industry.keys())
        industry_list.insert(0,'全行业')
        self.combo_industry['values'] = industry_list
        self.combo_industry.current(0)
        self._keyword_stocks()

    def load_data_source(self,source_name):
        with open('settings/'+source_name+'.txt','r',encoding='utf-8') as f:
            lines = f.readlines()
            stock_keys = []
            if len(lines)>0 and len(lines[0])>0:
                l = lines[0]
                if l[-1] == '\n':
                    l = l[:-1]
                    stock_keys = l.split(',')[1:]
                for l in lines[1:]:
                    if len(l)==0:
                        continue
                    if l[-1] == '\n':
                        l = l[:-1]
                    strs = l.split(',')
                    param = {}
                    for i in range(1, len(strs)):
                        param[stock_keys[i-1]] = strs[i]
                    self.stock_codes[strs[0].upper()] = param
                    if 'area' in param:
                        self.stock_area[param['area']]=0
                    if 'industry' in param:
                        self.stock_industry[param['industry']] = 0
            for k in stock_keys:
                if k not in self.stock_keys:
                    self.stock_keys.append(k)

    def _keyword_stocks(self):
        sns = []
        keyword_text = self.keyword_text.get().upper()
        self.list_stock.delete(0,self.list_stock.size())
        area = self.combo_area.get()
        industry = self.combo_industry.get()
        has_name = 'name' in self.stock_keys
        has_area = 'area' in self.stock_keys and area!='全区域'
        has_industry = 'industry' in self.stock_keys and industry!='全行业'
        for k in self.stock_codes:
            sn = k
            keyword_ok = False
            if keyword_text!='':
                if keyword_text in sn:
                    keyword_ok = True
                if has_name:
                    if keyword_text in self.stock_codes[k]['name']:
                        keyword_ok = True
            else:
                keyword_ok = True
            if keyword_ok is False:
                continue
            if has_area and area!=self.stock_codes[k]['area']:
                continue
            if has_industry and industry!=self.stock_codes[k]['industry']:
                continue
            if has_name:
                sn += ' ' + self.stock_codes[k]['name']
            sns.append(sn)
            self.list_stock.insert('end', sn)
#        self.list_stock.select_set(0)
#        sels = self.list_stock.curselection()#.split(' ')[0]
#        if len(sels)>0:
#            self.current_stock_code = self.list_stock.get(sels[0]).split(' ')[0]

    def _reset(self):
        self.sd = None
        self.data_sources = []
        self.current_data_source = ''
        self.stock_keys = []
        self.stock_codes = {}
        self.current_stock_code = ''
        self.current_segment_name = ''
        self.segments = {}
        self.freq = 'D'
        self.loaded = False
        self.range_sync = True
        self.from_time = 0
        self.to_time = time.time()
        self.select_time = 0
        shutil.rmtree('tmp',ignore_errors=True)

    def _load_stock(self):
        stock = self.sio.read_stock(self.current_stock_code, freq=self.freq)
        stock.name = self.stock_codes[self.current_stock_code]['name']
        self.sd = Stock_draw(stock, self.from_time, self.to_time, self.select_time)
        period = self.period.get()
        self.sd.change_freq(period)

    def _load_setting(self):
        fn = 'settings/setting.txt'
        with open(fn,'r',encoding='utf-8') as f:
            lines = f.readlines()
            for l in lines:
                if len(l)==0:
                    continue
                if l[-1] == '\n':
                    l = l[:-1]
                strs = l.split(':')
                if strs[0] == 'data':
                    self.data_sources.append(strs[1])
            vals = ['全部']
            vals.extend(self.data_sources)
            self.combo_source['values'] = vals
            self.combo_source.current(0)
            self.current_data_source = self.combo_source.get()
        self.all_codes = load_all_codes(self.data_sources)
