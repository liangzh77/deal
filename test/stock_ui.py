from tkinter import Tk, Canvas

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

root = Tk()
root.attributes("-topmost", True)
root.attributes("-fullscreen", True)

w, h = root.winfo_screenwidth(), root.winfo_screenwidth()

canvas1 = Canvas(root)
canvas1.place(relx=0., rely=0., relwidth=0.5, relheight=0.5)
draw_line(canvas1, [(w*0.05, h*0.1), (w*0.15, h*0.2), (w*0.25, h*0.15), (w*0.35, h*0.25)])
draw_bar_chart(canvas1, [(20, 30, 40), (40, 30, 20), (30, 40, 30)])

canvas2 = Canvas(root)
canvas2.place(relx=0.5, rely=0., relwidth=0.5, relheight=0.5)
draw_line(canvas2, [(10, 20), (30, 40), (50, 30), (70, 50)])
draw_bar_chart(canvas2, [(20, 30, 40), (40, 30, 20), (30, 40, 30)])

canvas3 = Canvas(root)
canvas3.place(relx=0., rely=0.5, relwidth=0.5, relheight=0.5)
draw_line(canvas3, [(10, 20), (30, 40), (50, 30), (70, 50)])
draw_bar_chart(canvas3, [(20, 30, 40), (40, 30, 20), (30, 40, 30)])

canvas4 = Canvas(root)
canvas4.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5)
draw_line(canvas4, [(10, 20), (30, 40), (50, 30), (70, 50)])
draw_bar_chart(canvas4, [(20, 30, 40), (40, 30, 20), (30, 40, 30)])

root.mainloop()