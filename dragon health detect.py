from email.base64mime import header_length
from unicodedata import name
import pyautogui
import time
from ctypes import *
from PIL import Image
import keyboard
import sys
import win32api
import win32gui
import win32con
import keys

def get_color(x, y):
    gdi32 = windll.gdi32
    user32 = windll.user32
    hdc = user32.GetDC(None)  # 获取颜色值
    pixel = gdi32.GetPixel(hdc, x, y)  # 提取RGB值
    r = pixel & 0x0000ff
    g = (pixel & 0x00ff00) >> 8
    b = pixel >> 16
    return [r, g, b]

def imgsrc(x,y):
    #for i in range(100):
        #last_time=time.time()
        img = pyautogui.screenshot()
        #img.save('{}.png'.format(i))
        color = img.getpixel((x,y))
        print(color)
        #print(time.time()-last_time)

#1100-1460 330

#1545-1015=530 10 63
        
def dragonhealth():
    damage_count=[]
    total_damage=0
    health_list=[];pause_health_list=False
    health=200;last_health=200
    while True:
        last_time=time.time()
        img = pyautogui.screenshot()
        last_color=0 ; health_count= 0
        hwnd = win32gui.GetForegroundWindow()
        titlename = win32gui.GetWindowText(hwnd)
        if titlename != "Minecraft* 1.16.1 - Singleplayer":
            break
        for i in range(530):
            color = img.getpixel((1015+i,63))
            if (color[0]==last_color and i>=1) or i==0:
                health_count+=1
                last_color = color[0]
            else:
                break
        health=int(health_count/2.65)
        if health==last_health and (not pause_health_list) and total_damage<200:
            if len(health_list)>0:
                if health_list[-1]!=health:
                    health_list.append(health)
                    pause_health_list=True
            else:
                health_list.append(health)
                pause_health_list=True
        else:
            pause_health_list=False
            total_damage+=last_health-health
        last_health=health
        #print("{}".format(health))
        #print("FPS: {:.0f}".format(1/(time.time()-last_time)))
    health_list.append(0)
    print(health_list)
    for i in range(len(health_list)-1):
        damage_count.append(health_list[i]-health_list[i+1])
    print(damage_count)

if __name__ ==  '__main__':
    #getpos()
    time.sleep(3)
    dragonhealth()
