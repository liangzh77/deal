import os, sys
sys.path.append(os.getcwd())
import cv2
import numpy as np
from core.stock_io import stock_io, IOSource
from draw.stock_draw import Stock_draw
import tkinter as tk
from PIL import Image, ImageTk


sio = stock_io(IOSource.File)
stock = sio.read_stock('期货/IC主力连续',freq='D')
sd = Stock_draw(stock,-30, 0)

#cv2.imshow('',m)
#cv2.waitKey()
root = tk.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
m = np.zeros((int(height*0.9),int(width*0.8),3),dtype=np.uint8)
sd.draw(m)
#root.geometry("%dx%d" % (width, height-100))
canvas = tk.Canvas(root)
#root.attributes("-fullscreen", True)
#canvas = tk.Canvas(root,width=1800,height=900)
canvas.pack(fill ="both", expand = True)
def _photo_image(image: np.ndarray):
    height, width = image.shape[:2]
    ppm_header = f'P6 {width} {height} 255 '.encode()
    data = ppm_header + cv2.cvtColor(image, cv2.COLOR_BGR2RGB).tobytes()
    return tk.PhotoImage(width=width, height=height, data=data, format='PPM')

img = _photo_image(m)
img_label = tk.Label(canvas, image=img)
img_label.pack(side=tk.RIGHT)
#canvas.update()

def hello():
    sd.set_range(-300,-30)
    sd.draw(m)
    img = _photo_image(m)
    img_label.configure(image=img)
    img_label.image = img
#    canvas.update()

tk.Button(canvas, text='hi                     ', command=hello).pack(side=tk.LEFT)
canvas.mainloop()