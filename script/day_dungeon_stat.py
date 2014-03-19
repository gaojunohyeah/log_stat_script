#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import xlrd
import time
import datetime
import os
import uuid
from elasticsearch import Elasticsearch
import sys
# 基础变量
gameCode = "pokersg"
serverId = "1001"
regionId = "1"
timestamp = str(long(time.time() * 1000))
yestodayLogName = "." + str(datetime.date.today() - datetime.timedelta(days=1)) + ".log"
if (len(sys.argv) == 4):
    gameCode = str(sys.argv[1])
    regionId = str(sys.argv[2])
    serverId = str(sys.argv[3])
# elasticsearch 连接参数
es_host = 'localhost'
index_name = 'stat_log-' + time.strftime("%Y.%m", )
statType = {
    'DUNGEON_PROCESS_STAT': 'dungeon_process_stat',
    'DUNGEON_TYPE_STAT': 'dungeon_type_stat',
    'DUNGEON_FAIL_STAT': 'dungeon_fail_stat'
}
doc = {
    'message': {
    },
    '@timestamp': timestamp,
    'type': ''
}
# 文件路径
# dungeon_log_path = "E:/work/workspace/sgpoker/logs/stat/dungeon_log.log"
dungeon_log_path = "/data/game_server/logs/stat/dungeon_log.log"

# dungeon_process_stat_path = "E:/work/workspace/sgpoker/logs/stat/dungeon_process_stat.log"
# dungeon_type_stat_path = "E:/work/workspace/sgpoker/logs/stat/dungeon_type_stat.log"
# dungeon_fail_stat_path = "E:/work/workspace/sgpoker/logs/stat/dungeon_fail_stat.log"
# user_operation_midfile_path = "E:/work/workspace/sgpoker/logs/stat/user_operate_midfile.log"
user_operation_midfile_path = "/data/game_server/logs/stat/user_operate_midfile.log"

# dungeon_excel_path = "E:/work/workspace/sgpoker_resources/config/common/dungeon.xls"
dungeon_excel_path = "/data/resources/config/common/dungeon.xls"
# stage_excel_path = "E:/work/workspace/sgpoker_resources/config/common/stage.xls"
stage_excel_path = "/data/resources/config/common/stage.xls"
# 关卡日志原因字典
dungeonLogReasonDic = {'DUNGEON_ENTER': 1101,
                       'DUNGEON_BRING_FRIEND': 1102,
                       'KILL_MONSTER': 1103,
                       'ENCOUNTER_MONSTER': 1104,
                       'ENCOUNTER_BOX_MONSTER': 1105,
                       'DUNGEON_COMPLETE': 1106,
                       'DUNGEON_FAIL': 1107,
                       'DUNGEON_EXIT': 1108}
# 其他静态常量
dungeonTypeDic = {1: 'NORMAL_DUNGEON',
                  2: 'ELITE_DUNGEON',
                  3: 'RESOURCE_DUNGEON',
                  4: 'ACTIVITY_DUNGEON'}
# 全局变量
# 关卡信息字典 格式: (key:int(id) , value:list(star,type)
dungeonInfoDic = {}
dungeonProcessStat = {}
dungeonTypeStat = {}
dungeonFailNumStat = {}
dungeonFailStarsStat = {}
dayDungeonTypeStatMap = {}
dayDungeonFailStatMap = {}
userOperationNumDic = {}

# 定义统计对象
# DungeonProcessStatBean
class DungeonProcessStatBean(object):
    def __init__(self, gameCode, serverId, regionId, timestamp, dungeonStar, completeNum):
        self.gameCode = gameCode
        self.serverId = serverId
        self.regionId = regionId
        self.timestamp = timestamp
        self.dungeonStar = dungeonStar
        self.completeNum = completeNum


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


# function : loadDungeonExcel
# 加载关卡excel配置信息到字典常量中
def loadDungeonExcel():
    global dungeonInfoDic

    # 加载关卡星级excel信息
    data = xlrd.open_workbook(dungeon_excel_path)
    table = data.sheets()[1]

    # 读取关卡星级
    ids = table.col_values(0)
    stars = table.col_values(1)
    for i in range(5, len(stars), 1):
        dungeonInfoDic[int(ids[i])] = []
        dungeonInfoDic[int(ids[i])].append(int(stars[i]))

    # 加载关卡类型excel信息
    data = xlrd.open_workbook(stage_excel_path)
    table = data.sheets()[3]

    # 读取关卡类型
    ids = table.col_values(0)
    types = table.col_values(3)
    for i in range(5, len(types), 1):
        if dungeonInfoDic.has_key(int(ids[i])):
            dungeonInfoDic[int(ids[i])].append(int(types[i]))


# function : dayDungeonStat
# 进行每日的关卡日志统计
def dayDungeonStat(jsonLine):
    # 如果是关卡完成类型的日志，则进行关卡进度统计以及关卡类型统计
    if jsonLine["message"]["reason"] == dungeonLogReasonDic["DUNGEON_COMPLETE"]:
        star = dungeonInfoDic[jsonLine["message"]["dungeonId"]][0]
        type = dungeonInfoDic[jsonLine["message"]["dungeonId"]][1]
        typeLabel = dungeonTypeDic[type]

        # 进行关卡类型统计
        if (not dungeonTypeStat.has_key(typeLabel)):
            dungeonTypeStat[typeLabel] = 0
        dungeonTypeStat[typeLabel] += 1

        # 进行关卡进度统计
        if (not dungeonProcessStat.has_key(star)):
            dungeonProcessStat[star] = set()
        dungeonProcessStat[star].add(jsonLine["message"]["charId"])

        # 添加关卡完成次数到用户操作统计中
        if (not userOperationNumDic.has_key("DUNGEON_COMPLETE")):
            userOperationNumDic["DUNGEON_COMPLETE"] = 0
        userOperationNumDic["DUNGEON_COMPLETE"] += 1
    # 如果是关卡失败类型的日志，则进行关卡死亡统计
    elif jsonLine["message"]["reason"] == dungeonLogReasonDic["DUNGEON_FAIL"]:
        star = dungeonInfoDic[jsonLine["message"]["dungeonId"]][0]
        type = dungeonInfoDic[jsonLine["message"]["dungeonId"]][1]
        typeLabel = dungeonTypeDic[type]

        # 进行关卡失败统计
        if (not dungeonFailNumStat.has_key(typeLabel)):
            dungeonFailNumStat[typeLabel] = 0
        dungeonFailNumStat[typeLabel] += 1
        if (not dungeonFailStarsStat.has_key(typeLabel)):
            dungeonFailStarsStat[typeLabel] = {}
        if (not dungeonFailStarsStat[typeLabel].has_key(star)):
            dungeonFailStarsStat[typeLabel][star] = 0
        dungeonFailStarsStat[typeLabel][star] += 1

        # 添加关卡失败次数到用户操作统计中
        if (not userOperationNumDic.has_key("DUNGEON_COMPLETE")):
            userOperationNumDic["DUNGEON_COMPLETE"] = 0
        userOperationNumDic["DUNGEON_COMPLETE"] += 1


# 加载关卡excel配置信息
loadDungeonExcel()

# 是否存在昨天的日志文件，如果没有，则读取目前的日志文件
if os.path.exists(dungeon_log_path + yestodayLogName):
    dungeon_log_path += yestodayLogName
# 读取关卡日志文件开始进行关卡日志统计
for line in open(dungeon_log_path):
    jsonLine = logtojson(line, )
    # 统计关卡日志
    dayDungeonStat(jsonLine)


# # output dungeon_process_stat into log file
# dungeon_process_stat_file = open(dungeon_type_stat_path, 'a')
# try:
#     for key, value in dungeonProcessStat.items():
#         dungeon_process_stat_object = DungeonProcessStatBean(gameCode, serverId, regionId, timestamp, key, len(value))
#         dungeon_process_stat_log = object2dict(dungeon_process_stat_object)
#         dungeon_process_stat_file.write(("{'message':" + str(dungeon_process_stat_log) + "}").replace("'", "\"") + "\n")
# finally:
#     dungeon_process_stat_file.close()


# # output day_dungeon_fail_stat into log file
# dayDungeonTypeStatMap["gameCode"] = gameCode
# dayDungeonTypeStatMap["serverId"] = serverId
# dayDungeonTypeStatMap["regionId"] = regionId
# dayDungeonTypeStatMap["timestamp"] = timestamp
# for key, value in dungeonTypeStat.items():
#     dayDungeonTypeStatMap[key] = value
# dungeon_type_stat_file = open(dungeon_type_stat_path, 'a')
# try:
#     dungeon_type_stat_file.write(("{'message':" + json.dumps(dayDungeonTypeStatMap) + "}").replace("'", "\"") + "\n")
# finally:
#     dungeon_type_stat_file.close()


# # output day_dungeon_type_stat into log file
# for key, value in dungeonFailNumStat.items():
#     dayDungeonFailStatMap.clear()
#     dayDungeonFailStatMap["gameCode"] = gameCode
#     dayDungeonFailStatMap["serverId"] = serverId
#     dayDungeonFailStatMap["regionId"] = regionId
#     dayDungeonFailStatMap["timestamp"] = timestamp
#     dayDungeonFailStatMap["dungeonType"] = key
#     dayDungeonFailStatMap["dungeonFailNum"] = value
#     for key, value in dungeonFailStarsStat[key].items():
#         dayDungeonFailStatMap["failStar" + key] = value
# dungeon_fail_stat_file = open(dungeon_fail_stat_path, 'a')
# try:
#     dungeon_fail_stat_file.write(("{'message':" + json.dumps(dayDungeonFailStatMap) + "}").replace("'", "\"") + "\n")
# finally:
#     dungeon_fail_stat_file.close()


# 输出关卡操作统计数据至用户操作中间文件
card_operate_file = open(user_operation_midfile_path, 'a')
try:
    for key, value in userOperationNumDic.items():
        card_operate_file.write("{\"" + str(key) + "\":" + str(value) + "}\n")
finally:
    card_operate_file.close()


# 初始化ES连接
es = Elasticsearch([
    {'host': es_host},
])


# 关卡进度统计
# 向ES中put统计数据
doc['type'] = statType['DUNGEON_PROCESS_STAT']
doc['message'] = {}
for key, value in dungeonProcessStat.items():
    dungeon_process_stat_object = DungeonProcessStatBean(gameCode, serverId, regionId, timestamp, key, len(value))
    doc['message'] = object2dict(dungeon_process_stat_object)
    res = es.index(index=index_name, doc_type=doc['type'], id=uuid.uuid1(), body=doc)
    if (not res['ok']):
        print "Elasticsearch put Error : timestamp->%s index->%s type->%s doc->%s" % (
            time.strftime("%Y-%m-%d %H:%M:%S", ), index_name, statType, doc)


# 封装关卡类型统计对象
dayDungeonTypeStatMap["gameCode"] = gameCode
dayDungeonTypeStatMap["serverId"] = serverId
dayDungeonTypeStatMap["regionId"] = regionId
dayDungeonTypeStatMap["timestamp"] = timestamp
# for key, value in dungeonTypeStat.items():
#     dayDungeonTypeStatMap[key] = value
# 封装ES对象
doc['type'] = statType['DUNGEON_TYPE_STAT']
# 向ES中put统计数据
for key, value in dungeonTypeStat.items():
    dayDungeonTypeStatMap["dungeonType"] = key
    dayDungeonTypeStatMap["completeNum"] = value
    doc['message'] = {}
    for key, value in dayDungeonTypeStatMap.items():
        doc['message'][key] = value
    res = es.index(index=index_name, doc_type=doc['type'], id=uuid.uuid1(), body=doc)
    if (not res['ok']):
        print "Elasticsearch put Error : timestamp->%s index->%s type->%s doc->%s" % (
            time.strftime("%Y-%m-%d %H:%M:%S", ), index_name, statType, doc)


# 封装关卡失败统计对象
for key, value in dungeonFailNumStat.items():
    dayDungeonFailStatMap.clear()
    dayDungeonFailStatMap["gameCode"] = gameCode
    dayDungeonFailStatMap["serverId"] = serverId
    dayDungeonFailStatMap["regionId"] = regionId
    dayDungeonFailStatMap["timestamp"] = timestamp
    dayDungeonFailStatMap["dungeonType"] = key
    dayDungeonFailStatMap["dungeonFailNum"] = value
    for key, value in dungeonFailStarsStat[key].items():
        dayDungeonFailStatMap["failStar_" + str(key)] = value
    # 封装ES对象
    doc['type'] = statType['DUNGEON_FAIL_STAT']
    doc['message'] = {}
    for key, value in dayDungeonFailStatMap.items():
        doc['message'][key] = value
    # 向ES中put统计数据
    res = es.index(index=index_name, doc_type=doc['type'], id=uuid.uuid1(), body=doc)
    if (not res['ok']):
        print "Elasticsearch put Error : timestamp->%s index->%s type->%s doc->%s" % (
            time.strftime("%Y-%m-%d %H:%M:%S", ), index_name, statType, doc)


