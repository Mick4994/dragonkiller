# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 21:10:06 2021

@author: pang
"""

from cgitb import reset
from selectors import EpollSelector
import numpy as np
from grabscreen import grab_screen
import cv2
import time
import keys
import random
from DQN_tensorflow_gpu import DQN
import os
import pandas as pd
import random
import tensorflow.compat.v1 as tf

def take_action(action):
    if action == 0:     # 跳过
        pass
    elif action == 1:   # 炸床
        keys.bed()

def blood_count(blood_gray_list):
    bloodnum=0
    for count in blood_gray_list:
        if count == 92 or count == 48:
            bloodnum+=1
    else:
        return 0,True
    return int(bloodnum/359*200),False

def damage_count(last_static_health,last_health,health,static_health):
    if last_health==health:
        if static_health:
            return 0,static_health,last_static_health
        else:
            static_health=True
            damage=last_static_health-health
            last_static_health=health
            return damage,static_health,last_static_health
    else:
        static_health=False
        return 0,static_health,last_static_health

def beduse_action_value(damage,total_damage):
    if total_damage<200:
        if damage == 0:
            return -30,False
        if damage>0 and damage<10:
            return -20,False
        if damage>=10 and damage<30:
            return 5,False
        if damage>=30 and damage<50:
            return 25,False
        if damage>=50 and damage<55:
            return 50,False
        if damage>=55 and damage<65:
            return 100,False            
    else:
        return 50,True

DQN_model_path = "model_gpu_5"
DQN_log_path = "logs_gpu/"
WIDTH = 213
HEIGHT = 120
mc_window_size = (853,300,1707,780)#852 480   426 240   213 120  
# station mc_window_size   (853, 300) (1707, 780)
dragon_window_size=(1064,340,1476,568) #412 228   206 114   103 57

health_size = (1101,326,1457,326)
# used to get dragon health

action_size = 2

if __name__ == '__main__':
    keys.reset()
    agent = DQN(WIDTH, HEIGHT, action_size, DQN_model_path, DQN_log_path)
    # DQN init   
    # count DRAGON blood
    target_step = 0
    # used to update target Q network
    done = False
    total_reward = 0
    total_damage = 0
    damage_list=[]
    beduse = 0
    open_reward = False
    static_health=True
    last_health=200
    last_static_health=200
    last_time = time.time()
    while not done:
        screen_gray = cv2.cvtColor(grab_screen(mc_window_size),cv2.COLOR_BGR2GRAY) 
        # 获得龙的状态灰度图
        station = cv2.resize(screen_gray,(WIDTH,HEIGHT))
        # 然后缩放四倍
        station = np.array(station).reshape(-1,HEIGHT,WIDTH,1)[0]
        # 把灰度图的三维数组转为二维数组，其实就是去掉最外层数组括号
        blood_gray_list = cv2.cvtColor(grab_screen(health_size),cv2.COLOR_BGR2GRAY)
        # 获得血条的灰度列表
        health = blood_count(blood_gray_list)
        # 根据灰度列表计算血量
        # collect blood gray graph for count dragon blood
        action = agent.Choose_Action(station)
        #给状态，取动作
        take_action(action)
        if action==1:
            beduse+=1
            time.sleep(0.1)            
        # take station then the station change                
        last_station = station
        damage,static_health,last_static_health=damage_count(last_static_health,last_health,health,static_health)
        if beduse-len(damage_list)==1:
            damage_list.append(damage)
            total_damage+=damage
            reward, done = beduse_action_value(damage,total_damage)
            damage=0
            total_reward+=reward
        last_health = health
        print('{}FPS'.format(int(1/(time.time()-last_time))))
        # get action reward
        
        
            
            
            
            
            
        
        
    
    