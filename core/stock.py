import numpy as np
import math
import datetime

class Stock:
    loaded = False
    ts_code = ''
    name = ''
    freq = ''
    freq_secs = 0
    times = np.zeros(0)
    opens = np.zeros(0)
    closes = np.zeros(0)
    highs = np.zeros(0)
    lows = np.zeros(0)
    volume = np.zeros(0)
    amount = np.zeros(0)
    k_show = np.ones(0)

    def set(self, ts_code, freq, times, opens, closes, highs, lows, volume, amount):
        self.ts_code = ts_code
        self.freq = freq
        if freq == '1min':
            self.freq_secs = 60
        if freq == 'D':
            self.freq_secs = 60*60*24

        if opens is None:
            self.opens=self.highs=self.lows=self.volume=self.amount=None
            self.times = self._set_nan_to_0(times)
            self.closes = self._set_nan_to_0(closes)
        else:
            opens = self._set_nan_to_0(opens)
            closes = self._set_nan_to_0(closes)
            highs = self._set_nan_to_0(highs)
            lows = self._set_nan_to_0(lows)
            volume = self._set_nan_to_0(volume)
            amount = self._set_nan_to_0(amount)
            min_size = min(opens.shape[0], closes.shape[0], highs.shape[0], lows.shape[0], volume.shape[0], amount.shape[0])
            self.times = times[-min_size:]
            self.opens = opens[-min_size:]
            self.closes = closes[-min_size:]
            self.highs = highs[-min_size:]
            self.lows = lows[-min_size:]
            self.volume = volume[-min_size:]
            self.amount = amount[-min_size:]
        self.ma5 = self.ma(5)
        self.ma10 = self.ma(10)
        self.ma20 = self.ma(20)
        self.k_show = np.ones(self.times.shape)
        self.loaded = True

    def _set_nan_to_0(self,v):
        if v is None:
            return None
        for i in range(v.shape[0]-1,-1,-1):
            if math.isnan(v[i]):
                v = v[i+1:]
                break
        return v

    def append(self, stock):
        if self.ts_code!=stock.ts_code:
            print('[error], stock, append(), ts_code are not the same')
            exit(1)
        if self.freq!=stock.freq:
            print('[error], stock, append(), freq are not the same')
            exit(1)
        self.times = np.hstack((self.times, stock.times))
        self.opens = np.hstack((self.opens, stock.opens))
        self.closes = np.hstack((self.closes, stock.closes))
        self.highs = np.hstack((self.highs, stock.highs))
        self.lows = np.hstack((self.lows, stock.lows))
        self.volume = np.hstack((self.volume, stock.volume))
        self.amount = np.hstack((self.amount, stock.amount))
        self.ma5 = self.ma(5)
        self.ma10 = self.ma(10)
        self.ma20 = self.ma(20)

    def length(self):
        return self.times.shape[0]

    def ma(self,sz):
        val = self.closes.copy()
        size = self.closes.shape[0]
        for i in range(0,sz-1):
            if i>=val.shape[0]:
                break
            val[i] = -1
        for i in range(sz-1, size):
            val[i] = np.mean(self.closes[i - (sz - 1):i + 1])
        return val

    def clear(self):
        self.loaded = False
        self.times = np.zeros(0)
        self.opens = np.zeros(0)
        self.closes = np.zeros(0)
        self.highs = np.zeros(0)
        self.lows = np.zeros(0)
        self.volume = np.zeros(0)
        self.amount = np.zeros(0)

    def clone(self, s=None):
        if s is None:
            s = Stock()
            s.clone(self)
            return s
        self.loaded = s.loaded
        self.ts_code = s.ts_code
        self.freq = s.freq
        self.freq_secs = s.freq_secs
        self.times = s.times.copy()
        self.opens = s.opens.copy()
        self.closes = s.closes.copy()
        self.highs = s.highs.copy()
        self.lows = s.lows.copy()
        self.volume = s.volume.copy()
        self.amount = s.amount.copy()

    def change_freq(self, freq):
        orig_len = self.length()
        if orig_len==0:
            return
        times = []
        opens = []
        closes = []
        highs = []
        lows = []
        volume = []
        amount = []
        secs_of_day = 60 * 60 * 24
        o=h=v=a=0
        l = 1e10
        last_t = self.times[0]
        dt2 = datetime.datetime.fromtimestamp(self.times[0])
        if self.opens.shape[0]==0:
            for i in range(orig_len):
                t = self.times[i]
                dt = datetime.datetime.fromtimestamp(self.times[i])
                if i+1<orig_len:
                    dt2 = datetime.datetime.fromtimestamp(self.times[i+1])
                if  i+1==orig_len \
                    or freq == 'day' and dt.day != dt2.day \
                    or freq == 'week' and (dt.weekday() == 0 or dt2.weekday() + (t - last_t) / secs_of_day > 6) \
                    or freq == 'month' and dt.month != dt2.month \
                    or freq == 'season' and dt.month != dt2.month and dt.month in (1, 4, 7, 10) \
                    or freq == 'year' and dt.year != dt2.year :
                    times.append(t)
                    closes.append(self.closes[i])
                else:
                    aaa=1
                last_t = t

        else:
            for i in range(orig_len):
                t = self.times[i]
                dt = datetime.datetime.fromtimestamp(self.times[i])
                if i+1<orig_len:
                    dt2 = datetime.datetime.fromtimestamp(self.times[i+1])
                if o==0:
                    o = self.opens[i]
                h = max(h, self.highs[i])
                l = min(l, self.lows[i])
                v += self.volume[i]
                a += self.amount[i]
                if  i+1==orig_len \
                    or freq == 'day' and (dt.day != dt2.day or dt.month!=dt2.month) \
                    or freq == 'week' and (dt.weekday() == 0 or dt2.weekday() + (t - last_t) / secs_of_day > 6) \
                    or freq == 'month' and dt.month != dt2.month \
                    or freq == 'season' and dt.month != dt2.month and dt.month in (1, 4, 7, 10) \
                    or freq == 'year' and dt.year != dt2.year :
                    times.append(t)
                    opens.append(o)
                    closes.append(self.closes[i])
                    highs.append(h)
                    lows.append(l)
                    volume.append(v)
                    amount.append(a)
                    o = h = v = a = 0
                    l = 1e10

                last_t = t

        if freq=='day':
            self.freq = 'D'
            self.freq_secs = secs_of_day
        if freq=='week':
            self.freq = 'W'
            self.freq_secs = secs_of_day*7
        if freq=='month':
            self.freq = 'M'
            self.freq_secs = secs_of_day*30
        if freq=='season':
            self.freq = 'S'
            self.freq_secs = secs_of_day*90
        if freq=='year':
            self.freq = 'Y'
            self.freq_secs = secs_of_day*365
        self.times = np.array(times)
        self.closes = np.array(closes)
        if self.opens is None:
            self.opens = None
            self.highs = None
            self.lows = None
            self.volume = None
            self.amount = None
        else:
            self.opens = np.array(opens)
            self.highs = np.array(highs)
            self.lows = np.array(lows)
            self.volume = np.array(volume)
            self.amount = np.array(amount)
        self.ma5 = self.ma(5)
        self.ma10 = self.ma(10)
        self.ma20 = self.ma(20)
