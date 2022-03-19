# -*- coding: utf-8 -*-
"""
@author: Mick4994
"""

import numpy as np
from grabscreen import grab_screen
import cv2
import time
import keys
from DQN_tensorflow_gpu import DQN
import os
import pandas as pd
import random
import keys
import tensorflow.compat.v1 as tf
import win32api
import win32gui
import win32con

def isMinecraft():
    hwnd = win32gui.GetForegroundWindow()
    titlename = win32gui.GetWindowText(hwnd)
    if titlename != "Minecraft* 1.16.1 - Singleplayer":
        return False
    else:
        return True

def take_action(action):
    if action == 0:     # 缓冲
        time.sleep(0.1)
    elif action == 1:   # 炸床
        keys.bed()
    '''elif action == 2:   #炸床间隔
        time.sleep(1.5)'''

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

def damage_count(healthlist,last_health,health,static_health):#已弃用该函数
    if last_health==health:
        if static_health:
            return 0,static_health
        else:
            static_health=True
            return healthlist-health,static_health
    else:
        static_health=False
        return 0,static_health

def beduse_action_value(damage,total_damage,beduse):#计算每次炸床获得的奖励
    if total_damage<200:
        '''if damage == 0:
            reward=-10
        elif damage>0 and damage<10:
            reward=10
        elif damage>=10 and damage<35:
            reward=15
        elif damage>=35 and damage<40:
            reward=30
        elif damage>=40 and damage<45:
            reward=60
        elif damage>=45 and damage<50:
            reward=150
        elif damage>=50 and damage<55:
            reward=275
        elif damage>=55 and damage<65:
            reward=500
        else:
            reward=-30'''
        #return reward-(beduse*2),0
        return damage,0            
    else:
        #reward = 50
        #return reward-(beduse*2),1 
        return damage,1 
        
def digital_station(dragon_window_size,health_size,need):#输入龙的图像，血量图像，cv2灰度化和np数组处理，返回：龙，血的数组
    screen_gray = cv2.cvtColor(grab_screen(dragon_window_size),cv2.COLOR_BGR2GRAY) 
    # 获得龙的状态灰度图
    obs_dragon = cv2.resize(screen_gray,(WIDTH,HEIGHT))
    # 然后缩放四倍
    obs_dragon = np.array(obs_dragon).reshape(-1,HEIGHT,WIDTH,1)[0]
    # 把灰度图的三维数组转为二维数组，其实就是去掉最外层数组括号
    blood_gray_list = cv2.cvtColor(grab_screen(health_size),cv2.COLOR_BGR2GRAY)[0]
    # 获得血条的灰度列表
    health = blood_count(blood_gray_list)
    # 根据灰度列表计算血量
    # collect blood gray graph for count dragon blood
    if need == 'health':
        return health
    elif need =='obs_dragon':
        return obs_dragon
    elif need =='both':
        return obs_dragon,health

DQN_model_path = "model_gpu"
DQN_log_path = "logs_gpu/"

WIDTH = 104
HEIGHT = 56

mc_window_size = (853,300,1707,780)#852 480   426 240   213 120  
# station window_size   (853, 300) (1707, 780)
#dragon_window_size=(1064,340,1476,568) #412 228   206 114   103 57    
dragon_window_size=(1062,342,1478,566) #416 224    208 112   104 56   52 28   26 14
#412 turn to 416    228 turn to 224

health_size = (1101,326,1456,326)
# used to get dragon health

action_size = 2  #do nothing and use bed

EPISODES = 100
big_BATCH_SIZE = 16
UPDATE_STEP = 10
# times that evaluate the network
num_step = 0
# used to save log graph
target_step = 0
# used to update target Q network

if __name__ == '__main__':
    keys.resetkeys()
    agent = DQN(WIDTH, HEIGHT, action_size, DQN_model_path, DQN_log_path)
    # DQN init
    for episode in range(EPISODES):
        count_step = 0 #计算每回步数
        # used to update target Q network
        done = 0 #False ：回合是否完成
        total_reward = 0
        reward=0
        total_damage = 0
        damage=0
        beduse = 0
        health = 200
        print('start:',episode+1)
        while not done:
            if not isMinecraft():#如果不在MC窗口，停止训练
                break
            obs_dragon,health= digital_station(dragon_window_size,health_size,'both')
            if health == 0 and not done:
                reward=200-total_damage
                done=1
            if not done:
                action = agent.Choose_Action(obs_dragon)
                #给状态，取动作
                take_action(action)
                print('action:',action)
                if action==1:#1是采取炸床
                    beduse+=1
                    print('beduse:',beduse)
                    time.sleep(1.6)
                    next_health=digital_station(dragon_window_size,health_size,'health')
                    damage=health-next_health
                    total_damage+=damage
                    print('health:',health,'damage:{}'.format(damage))
                    reward, done = beduse_action_value(damage,total_damage,beduse)
                    #根据伤害获取炸床奖励，并根据累记伤害返回是否完成将末影龙击杀
                else:
                    reward=-beduse
            next_obsdragon= digital_station(dragon_window_size,health_size,'obs_dragon')
            agent.Store_Data(obs_dragon, action, reward, next_obsdragon, done)
            if len(agent.replay_buffer) > big_BATCH_SIZE:
                num_step += 1
                # save loss graph
                # print('train')
                agent.Train_Network(big_BATCH_SIZE, num_step)
            if target_step % UPDATE_STEP == 0:
                agent.Update_Target_Network()
                # update target Q network
            total_reward += reward
            #初始化所有步骤参数：
            damage=0
            reward=0
            if total_damage>=200:
                done=1#True            
            count_step+=1
            target_step+=1
            print('health:',health,'count_step:',count_step)
        if episode % 5 == 0:
            agent.save_model()
            # save model
        if target_step!=0 and beduse!=0:
            print('episode: ', episode+1, 'Average Beduse Reward:{:.2f}'.format(total_reward/beduse))
            print('total_reward: ', total_reward,'beduse:',beduse,'total_damage:',total_damage)
        else:
            print('episode: ', episode+1,'fail and do nothing ','total_reward: ', total_reward)
        if not isMinecraft():
            print("Training is destroyed")#训练被破坏
            
            break
        #time.sleep(8)
        keys.resetkeys()
        print('reset')
        
            
            
            
            
            
        
        
    
    