import sys, os, pickle
script_dir = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(script_dir)
base_dir = os.path.split(script_dir)[0]
sys.path.append(base_dir)
from stock_tool import *
from tkinter import Tk, Canvas

fn = 'settings/a股个股.txt'
codes = load_codes_from_file(fn)

stocks = Stocks()
codes2 = {key: codes[key] for key in list(codes.keys())[:100]}
#selected = temp_load_pkl()
selected = filter_stock4(stocks, codes2)
code_index=0


def draw_line(canvas, points):
    # 模拟绘制折线数据
#    points = [(10, 20), (30, 40), (50, 30), (70, 50)]
    for i in range(len(points) - 1):
        canvas.create_line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])

def draw_bar_chart(canvas, bars):
    # 模拟绘制柱状图数据
#    bars = [(20, 30, 40), (40, 30, 20), (30, 40, 30)]
    for i, bar in enumerate(bars):
        x = 10 + i * 30
        for j, height in enumerate(bar):
            y = 100 - height
            canvas.create_rectangle(x, y, x + 20, 100, fill='blue')

def key_press(event):
    global code_index
    if event.keysym == 'Left':
        code_index = max(0, code_index-1)
    if event.keysym == 'Right':
        code_index = min(len(selected)-1, code_index+1)
    draw_fenshi(canvas1, code_index, -1)
    draw_fenshi(canvas2, code_index, 0)
    draw_fenshi(canvas3, code_index, 1)

def draw_fenshi(can, index, day_offset):
    can.delete("all")
    keys = list(selected.keys())
    code_name = keys[index]
    code = selected[code_name]
    stock = code['stock']
    day = stock.info['day']
    day_ind = day['timev'].index(code['date'])+day_offset
    min5=stock.info['min5'][day['timev'][day_ind]]
    closev = min5['closev']
    basev = day['closev'][day_ind-1]
    w, h = can.winfo_width(), can.winfo_height()
    lines = []
    if code_name[2:4] in ['30','68']:
        rg = 0.2
    else:
        rg = 0.1
    maxv, minv = basev*(1+rg+0.01), basev*(1-rg-0.01)
    dif = maxv-minv
    for i, v in enumerate(min5['closev']):
        x = w/48*i
        y = h-h*(v-minv)/dif
        lines.append((x,y))
    draw_line(can, lines)
    draw_line(can, [(0,h/2),(w,h/2)])
    draw_line(can, [(w/48*23,h*0),(w/48*23,h*1)])
#    draw_bar_chart(can, [(20, 30, 40), (40, 30, 20), (30, 40, 30)])
    

root = Tk()
root.attributes("-topmost", True)
root.attributes("-fullscreen", True)

w, h = root.winfo_screenwidth(), root.winfo_screenwidth()

canvas1 = Canvas(root)
canvas1.place(relx=0.5, rely=0., relwidth=0.5, relheight=1/3)
canvas2 = Canvas(root)
canvas2.place(relx=0.5, rely=1/3, relwidth=0.5, relheight=1/3)
canvas3 = Canvas(root)
canvas3.place(relx=0.5, rely=2/3, relwidth=0.5, relheight=1/3)

root.bind("<Key>", key_press)

root.mainloop()