#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import xlrd
import time
import datetime
import uuid
from elasticsearch import Elasticsearch
# 基础变量
gameCode = "pokersg"
serverId = "1001"
regionId = "1"
timestamp = str(long(time.time() * 1000))
yestodayLogName = "." + str(datetime.date.today() - datetime.timedelta(days=1)) + ".log"
# 文件路径
player_log_path = "E:/work/workspace/sgpoker/logs/stat/player_log.log"

# 玩家日志 原因 字典
playerLogReasonDic = {'PL_CJ': 101,  # 角色创建
                      'PL_SC': 102,  # 角色删除
                      'PL_ZY': 103,  # 角色转移
                      'PL_DL': 104,  # 登录
                      'PL_DC': 105,  # 登出
                      'PL_AUTO_NAME': 106,  # 角色创建自动起名
                      'PL_CJ_START': 107,  # 角色创建开始
                      'PL_STOP': 108,  # 角色封停
                      'PL_MUTE': 109,  # 角色禁言
                      'PL_DEVICE_IOS': 110,  # 登录设备(ios)
                      'PL_DEVICE_ANDROID': 111,  # 登录设备(ANDROID)
                      'PL_DEVICE_INFO': 112,  # 登录设备信息
                      'PL_EXP_GET': 113,  # 经验
                      'PL_LVL_UP': 114  # 升级
}




