# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 12:14:29 2020

@author: pang
"""

from time import sleep
import cv2
import numpy as np
import win32gui, win32ui, win32con, win32api
import pyautogui
import time
import keyboard
import keys

def grab_screen(region=None):

    hwin = win32gui.GetDesktopWindow()

    if region:
            left,top,x2,y2 = region
            width = x2 - left + 1
            height = y2 - top + 1
    else:
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
    
    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (height,width,4)

    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    return img

#dragon health position Point(x=1101, y=326)
#                       Point(x=1456, y=326)

def getmc():
    foundmc = False
    while not foundmc:
        hwnd = win32gui.GetForegroundWindow()
        titlename = win32gui.GetWindowText(hwnd)
        if titlename == "Minecraft* 1.16.1 - Singleplayer":
            #print(win32gui.GetClientRect(hwnd))#返回指定窗口客户区矩形的大小  854 480
            print(win32gui.ClientToScreen(hwnd,(854,480)))
            #判断窗口内以客户区坐标表示的一个点的屏幕坐标  (853, 300) (1707, 780)
            x1,y1,x2,y2=win32gui.GetClientRect(hwnd)
            #print(x2-x1,y2-y1)
            break

def testgray():
    #img = pyautogui.screenshot(region=window_size)
    #mc_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    #cv2.imshow('test',mc_gray)
    img_path='test4.png'
    img = cv2.imread(img_path)
    #获取图片的宽和高
    width,height = 854,480
    #将图片缩小便于显示观看
    #img_resize = cv2.resize(img,(int(width*0.5),int(height*0.5)),interpolation=cv2.INTER_CUBIC)
    img_size=(width,height)
    #cv2.imshow("img",img)
    #print("img_reisze shape:{}".format(np.shape(img_size)))

    #将图片转为灰度图 dragonhealth gray 92 and 43, 48
    #                losshealth gray 28 and 30, 34
    img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    for i in img_gray[26][246:606]:  #606-246+1 = 361  health_size = (1101,326,1457,326)
        print(i)
    cv2.imshow("img_gray",img_gray)
    #print("img_gray shape:{}".format(np.shape(img_gray)))
    cv2.waitKey(30000)

def blood_count(blood_gray_list):
    bloodnum=0
    for count in blood_gray_list:
        if count == 92 or count == 48:
            bloodnum+=1
    health=int(bloodnum/356*200)
    if health>=160 and health<200:
        adjust=-2
    elif health>=140 and health<160:
        adjust=-1
    elif health>=100 and health<140:
        adjust=0
    elif health>=60 and health<100:
        adjust=1
    elif health>=40 and health<60:
        adjust=2
    elif health>=3 and health<40:
        adjust=3
    else:
        adjust=0
    return health+adjust

if __name__ == '__main__':
    WIDTH = 103
    HEIGHT = 57
    health_size = (1101,326,1456,326)
    dragon_window_size=(1064,340,1476,568) #412 228   206 114   103 57
    time.sleep(3)
    #screen_gray = cv2.cvtColor(grab_screen(dragon_window_size),cv2.COLOR_BGR2GRAY)
    #print(np.array(screen_gray))
    #print(np.array(grab_screen(dragon_window_size)))
    #station = cv2.resize(screen_gray,(WIDTH,HEIGHT))
    #cul_station = np.array(station).reshape(-1,HEIGHT,WIDTH,1)[0]
    #for i in range(4):
    #blood_gray_list = cv2.cvtColor(grab_screen(health_size),cv2.COLOR_BGR2GRAY)[0]
        # 获得血条的灰度列表
    #health = blood_count(blood_gray_list)
    #print(blood_gray_list)
    #print(health)
        #time.sleep(1.5)
    #testgray()
    #getmc()
    count=0
    while True:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        if title == 'Minecraft* 1.16.1 - Singleplayer':
            blood_gray_list = cv2.cvtColor(grab_screen(health_size),cv2.COLOR_BGR2GRAY)[0]
            # 获得血条的灰度列表
            health = blood_count(blood_gray_list)
            keys.test_FPS()
            time.sleep(0.5)
            count+=1
            print('count:',count,'health:',health)
        else:
            break