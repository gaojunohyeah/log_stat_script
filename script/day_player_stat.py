#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import time
import datetime
import os
from elasticsearch import Elasticsearch
import sys
from dateutil import rrule
# 基础变量
gameCode = "pokersg"
serverId = "1001"
regionId = "1"
timestamp = str(long(time.time() * 1000))
todayZero = long(time.mktime(datetime.date.today().timetuple()) * 1000)
yestodayZero = long(time.mktime(datetime.date.today().timetuple()) * 1000)
yestodayLogName = "." + str(datetime.date.today() - datetime.timedelta(days=1)) + ".log"
twoDaysAgoLogName = "." + str(datetime.date.today() - datetime.timedelta(days=2)) + ".log"
if (len(sys.argv) == 4):
    gameCode = str(sys.argv[1])
    regionId = str(sys.argv[2])
    serverId = str(sys.argv[3])
# elasticsearch 连接参数
es_host = 'localhost'
index_name = 'stat_log-' + time.strftime("%Y.%m", )
statType = {
    'ONLINE_TIME_STAT': 'online_time_stat',
}
idsBody = {
    "ids":[]
}
doc = {
    'message': {
    },
    '@timestamp': timestamp,
    'type': ''
}
# 文件路径
# player_log_path = "E:/work/workspace/sgpoker/logs/stat/player_log.log"
player_log_path = "/data/game_server/logs/stat/player_log.log"

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

# 全局变量
# 玩家登录登出统计 格式：{'accountId':[[loginTime,logoutTime],[loginTime,logoutTime]],'accountId':[[loginTime,logoutTime],[loginTime,logoutTime]]}
userLoginAndLogoutDic = {}
userBeanDic = {}


# 初始化ES连接
es = Elasticsearch([
    {'host': es_host},
])


# 定义统计对象
# UserOnlineTimeStatBean
class UserOnlineTimeStatBean(object):
    def __init__(self, gameCode, serverId, regionId, accountId, charId, charName,
                 totalOnlineTime, timestamp):
        self.gameCode = gameCode
        self.serverId = serverId
        self.regionId = regionId
        self.accountId = accountId
        self.charId = charId
        self.charName = charName
        self.totalOnlineTime = totalOnlineTime
        self.timestamp = timestamp


# function : logtojson
# 读取文件行转换为json对象
def logtojson(line):
    s = json.loads(line)
    return s


# 将object对象转换为字典
def object2dict(obj):
    d = {}
    #d["__class__"] = obj.__class__.__name__
    #d["__module__"] = obj.__module__
    d.update(obj.__dict__)
    return d


def datetimeFromTimestamp(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp/1000))


def minutes_between(start,end):
    minutes = rrule.rrule(rrule.MINUTELY, dtstart=datetimeFromTimestamp(start), until=datetimeFromTimestamp(end))
    return minutes.count()


# function : dayPlayerStat
# 统计玩家日志
def dayPlayerStat(jsonLine):
    accountId = jsonLine["message"]["accountId"]
    id = str(serverId+'_'+accountId)

    # 登录日志
    if jsonLine["message"]["reason"] == playerLogReasonDic['PL_DL']:
        if (not userLoginAndLogoutDic.has_key(id)):
            userLoginAndLogoutDic[id] = []
        size = len(userLoginAndLogoutDic[id])
        # 列表size为0 或者 列表最后一个元素的size为2
        if (size == 0 or len(userLoginAndLogoutDic[id][size - 1]) == 2):
            login = [jsonLine["message"]["logTime"]]
            userLoginAndLogoutDic[id].append(login)

        # 放置用户的对象信息
        if (not userBeanDic.has_key(id)):
            userBeanDic[id] = UserOnlineTimeStatBean(gameCode, serverId, regionId, accountId,
                                                            jsonLine["message"]["charId"],
                                                            jsonLine["message"]["charName"], 0, timestamp)

    # 登出日志
    if jsonLine["message"]["reason"] == playerLogReasonDic['PL_DC']:
        if (not userLoginAndLogoutDic.has_key(id)):
            userLoginAndLogoutDic[id] = []
        size = len(userLoginAndLogoutDic[id])
        # 列表size不为0 并且 列表最后一个元素的size为1 ， 则 追加登出时间
        if (size > 0 and len(userLoginAndLogoutDic[id][size - 1]) == 1):
            logout = jsonLine["message"]["logTime"]
            userLoginAndLogoutDic[id][size - 1].append(logout)
        # 列表size为0 ， 则 默认登录时间为当天0点，并追加登出时间
        elif size == 0:
            logout = [yestodayZero, jsonLine["message"]["logTime"]]
            userLoginAndLogoutDic[id].append(logout)

        # 放置用户的对象信息
        if (not userBeanDic.has_key(id)):
            userBeanDic[id] = UserOnlineTimeStatBean(gameCode, serverId, regionId, accountId,
                                                            jsonLine["message"]["charId"],
                                                            jsonLine["message"]["charName"], 0, timestamp)


# function : doOnlineTimeStat
# 进行在线时长统计
def doOnlineTimeStat():
    # 循环用户的登录登出时间字典
    for key, value in userLoginAndLogoutDic.items():
        onlineTime = 0
        for i in range(0, len(value), 1):
            if len(value[i]) == 1:
                onlineTime += minutes_between(value[i][0],todayZero)
            else:
                onlineTime += minutes_between(value[i][0],value[i][1])

        # 统计在线时长
        userBeanDic[key].totalOnlineTime = onlineTime
        idsBody['ids'].append(str(key))

    # 从ES中获取数据
    res = es.mget(body=idsBody,index=index_name, doc_type=statType['ONLINE_TIME_STAT'])
    for elem in res['docs']:
        if not elem.has_key('error'):
            if elem['exists']:
                userBeanDic[elem['_id']].totalOnlineTime += elem['_source']['message']['totalOnlineTime']

            # 更新或者插入统计数据
            doc['type'] = statType['ONLINE_TIME_STAT']
            doc['message'] = object2dict(userBeanDic[elem['_id']])
            res = es.index(index=index_name, doc_type=doc['type'], id=elem['_id'], body=doc)
            if (not res['ok']):
                print "Elasticsearch put Error : timestamp->%s index->%s type->%s doc->%s" % (
                    time.strftime("%Y-%m-%d %H:%M:%S", ), index_name, statType, doc)


# 是否存在昨天的日志文件，如果没有，则读取目前的日志文件
if os.path.exists(player_log_path + yestodayLogName):
    player_log_path += yestodayLogName
elif (not os.path.exists(player_log_path + twoDaysAgoLogName)):
    sys.exit()
# 读取玩家日志文件开始进行卡牌日志统计
for line in open(player_log_path):
    jsonLine = logtojson(line, )
    # 统计玩家日志
    dayPlayerStat(jsonLine)

doOnlineTimeStat()
# print todayZero
# for key, value in userLoginAndLogoutDic.items():
#     print key, value
# print 'a'
# 进行在线时长统计
# doOnlineTimeStat()



