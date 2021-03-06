#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import time
import datetime
import os
import sys
# 基础变量
gameCode = "pokersg"
serverId = "1001"
regionId = "1"
now = datetime.date.today()
d = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
timestamp = str(long(time.mktime(d.timetuple()) * 1000 - 1))
yestodayLogName = "." + str(datetime.date.today() - datetime.timedelta(days=1)) + ".log"
if (len(sys.argv) == 5):
    gameCode = str(sys.argv[1])
    regionId = str(sys.argv[2])
    serverId = str(sys.argv[3])
    timestamp = str(sys.argv[4])
if (len(sys.argv) == 4):
    gameCode = str(sys.argv[1])
    regionId = str(sys.argv[2])
    serverId = str(sys.argv[3])
# 文件路径
# gift_log_path = "E:/work/workspace/sgpoker/logs/stat/gift_log.log"
gift_log_path = "/data/game_server/logs/stat/gift_log.log"

# user_operation_midfile_path = "E:/work/workspace/sgpoker/logs/stat/user_operate_midfile.log"
user_operation_midfile_path = "/data/game_server/logs/stat/user_operate_midfile.log"
# 礼包日志 原因字典
giftLogReasonDic = {'GIFT_GET': 601,  # 礼包_获得
                    'GIFT_OPEN': 602,  # 礼包_打开
                    'GIFT_DELETE': 603  # 礼包_删除
}
# 全局变量
userOperationNumDic = {}

# function : logtojson
# 读取文件行转换为json对象
def logtojson(line):
    s = json.loads(line)
    return s


# function : dayGiftStat
# 统计礼包日志
def dayGiftStat(jsonLine):

    # 统计每日礼包操作次数数据
    if jsonLine["message"]["reason"] == giftLogReasonDic.get("GIFT_GET"):
        if (not userOperationNumDic.has_key("GIFT_GET")):
            userOperationNumDic["GIFT_GET"] = 0
        userOperationNumDic["GIFT_GET"] += 1


# 将object对象转换为字典
def object2dict(obj):
    d = {}
    #d["__class__"] = obj.__class__.__name__
    #d["__module__"] = obj.__module__
    d.update(obj.__dict__)
    return d


# 是否存在昨天的日志文件，如果没有，则读取目前的日志文件
if os.path.exists(gift_log_path + yestodayLogName):
    gift_log_path += yestodayLogName
# 读取卡牌日志文件开始进行卡牌日志统计
for line in open(gift_log_path):
    jsonLine = logtojson(line, )
    # 统计卡牌日志
    dayGiftStat(jsonLine)


# 输出卡牌操作统计数据至用户操作中间文件
user_operate_file = open(user_operation_midfile_path, 'a')
try:
    for key, value in userOperationNumDic.items():
        user_operate_file.write("{\"" + str(key) + "\":" + str(value) + "}\n")
finally:
    user_operate_file.close()





