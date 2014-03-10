#!/usr/bin/python
import json
import xlrd
import time
import datetime
import os
# init var of base
gameCode = "pokersg"
serverId = "1001"
regionId = "1"
timestamp = str(long(time.time() * 1000))
yestodayLogName = "." + str(datetime.date.today() - datetime.timedelta(days=1)) + ".log"
# init file path
dungeon_log_path = "E:/work/workspace/sgpoker/logs/stat/dungeon_log.log"

dungeon_process_stat_path = "E:/work/workspace/sgpoker/logs/stat/sscard_add_stat.log"
dungeon_type_stat_path = "E:/work/workspace/sgpoker/logs/stat/dungeon_type_stat.log"
dungeon_fail_stat_path = "E:/work/workspace/sgpoker/logs/stat/scard_source_stat.log"
user_operation_midfile_path = "E:/work/workspace/sgpoker/logs/stat/user_operate_midfile.log"

dungeon_excel_path = "E:/work/workspace/sgpoker_resources/config/common/dungeon.xls"
stage_excel_path = "E:/work/workspace/sgpoker_resources/config/common/stage.xls"
# dungeon_log reason dictionary
dungeonLogReasonDic = {'DUNGEON_ENTER': 1101,
                       'DUNGEON_BRING_FRIEND': 1102,
                       'KILL_MONSTER': 1103,
                       'ENCOUNTER_MONSTER': 1104,
                       'ENCOUNTER_BOX_MONSTER': 1105,
                       'DUNGEON_COMPLETE': 1106,
                       'DUNGEON_FAIL': 1107,
                       'DUNGEON_EXIT': 1108}
# other static constants
dungeonTypeDic = {1: 'NORMAL_DUNGEON',
                  2: 'ELITE_DUNGEON',
                  3: 'RESOURCE_DUNGEON',
                  4: 'ACTIVITY_DUNGEON'}
# global attribute
# dungeon info dictionary (key:int(id) , value:list(star,type)
dungeonInfoDic = {}
dungeonProcessStat = {}
dungeonTypeStat = {}
dungeonFailNumStat = {}
dungeonFailStarsStat = {}
dayDungeonTypeStatMap = {}
dayDungeonFailStatMap = {}
userOperationNumDic = {}

# define stat object
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
# load log file line to json object
def logtojson(line):
    # print line
    s = json.loads(line)
    return s


# transform object to dictionary
def object2dict(obj):
    d = {}
    #d["__class__"] = obj.__class__.__name__
    #d["__module__"] = obj.__module__
    d.update(obj.__dict__)
    return d


# function : loadDungeonExcel
# load dungeon into into dictionary static constants
def loadDungeonExcel():
    global dungeonInfoDic

    # load dungeon stars info
    data = xlrd.open_workbook(dungeon_excel_path)
    table = data.sheets()[1]

    # load dungeon stars
    ids = table.col_values(0)
    stars = table.col_values(1)
    for i in range(5, len(stars), 1):
        dungeonInfoDic[int(ids[i])] = []
        dungeonInfoDic[int(ids[i])].append(int(stars[i]))

    # load dungeon types info
    data = xlrd.open_workbook(stage_excel_path)
    table = data.sheets()[3]

    # load dungeon types
    ids = table.col_values(0)
    types = table.col_values(3)
    for i in range(5, len(types), 1):
        if dungeonInfoDic.has_key(int(ids[i])):
            dungeonInfoDic[int(ids[i])].append(int(types[i]))


# function : dayDungeonStat
# do day dungeon stat
def dayDungeonStat(jsonLine):
    # if dungeon complete log reason, do dungeon_process_stat and day_dungeon_type_stat
    if jsonLine["message"]["reason"] == dungeonLogReasonDic["DUNGEON_COMPLETE"]:
        star = dungeonInfoDic[jsonLine["message"]["reason"]][0]
        type = dungeonInfoDic[jsonLine["message"]["reason"]][1]
        typeLabel = dungeonTypeDic[type]

        # do day_dungeon_type_stat
        if (not dungeonTypeStat.has_key(typeLabel)):
            dungeonTypeStat[typeLabel] = 0
        dungeonTypeStat[typeLabel] += 1

        # do dungeon_process_stat
        if (not dungeonProcessStat.has_key(star)):
            dungeonTypeStat[star] = set()
        dungeonTypeStat[star].add(jsonLine["message"]["charId"])

        # add dungeon complete times to userOperationStat
        if (not userOperationNumDic.has_key("DUNGEON_COMPLETE")):
            userOperationNumDic["DUNGEON_COMPLETE"] = 0
        userOperationNumDic["DUNGEON_COMPLETE"] += 1
    # if dungeon fail log reason, do dungeon_fail_stat_path
    elif jsonLine["message"]["reason"] == dungeonLogReasonDic["DUNGEON_FAIL"]:
        star = dungeonInfoDic[jsonLine["message"]["reason"]][0]
        type = dungeonInfoDic[jsonLine["message"]["reason"]][1]
        typeLabel = dungeonTypeDic[type]

        # do dungeon_fail_stat_path
        if (not dungeonFailNumStat.has_key(typeLabel)):
            dungeonFailNumStat[typeLabel] = 0
        dungeonFailNumStat[typeLabel] += 1
        if (not dungeonFailStarsStat.has_key(typeLabel)):
            dungeonFailStarsStat[typeLabel] = {}
        if (not dungeonFailStarsStat[typeLabel][star]):
            dungeonFailStarsStat[typeLabel][star] = 0
        dungeonFailStarsStat[typeLabel][star] += 1

        # add dungeon fail times to userOperationStat
        if (not userOperationNumDic.has_key("DUNGEON_COMPLETE")):
            userOperationNumDic["DUNGEON_COMPLETE"] = 0
        userOperationNumDic["DUNGEON_COMPLETE"] += 1


# load gacha excel config info
loadDungeonExcel()

if os.path.exists(dungeon_log_path + yestodayLogName):
    dungeon_log_path += yestodayLogName
# do stat
for line in open(dungeon_log_path):
    jsonLine = logtojson(line, )
    # stat dungeon log info
    dayDungeonStat(jsonLine)


# output dungeon_process_stat into log file
dungeon_process_stat_file = open(dungeon_type_stat_path, 'a')
try:
    for key, value in dungeonProcessStat.items():
        dungeon_process_stat_object = DungeonProcessStatBean(gameCode, serverId, regionId, timestamp, key, len(value))
        dungeon_process_stat_log = object2dict(dungeon_process_stat_object)
        dungeon_process_stat_file.write(("{'message':" + str(dungeon_process_stat_log) + "}").replace("'", "\"") + "\n")
finally:
    dungeon_process_stat_file.close()


# output day_dungeon_fail_stat into log file
dayDungeonTypeStatMap["gameCode"] = gameCode
dayDungeonTypeStatMap["serverId"] = serverId
dayDungeonTypeStatMap["regionId"] = regionId
dayDungeonTypeStatMap["timestamp"] = timestamp
for key, value in dungeonTypeStat.items():
    dayDungeonTypeStatMap[key] = value
dungeon_type_stat_file = open(dungeon_type_stat_path, 'a')
try:
    dungeon_type_stat_file.write(("{'message':" + json.dumps(dayDungeonTypeStatMap) + "}").replace("'", "\"") + "\n")
finally:
    dungeon_type_stat_file.close()


# output day_dungeon_type_stat into log file
for key, value in dungeonFailNumStat.items():
    dayDungeonFailStatMap.clear()
    dayDungeonFailStatMap["gameCode"] = gameCode
    dayDungeonFailStatMap["serverId"] = serverId
    dayDungeonFailStatMap["regionId"] = regionId
    dayDungeonFailStatMap["timestamp"] = timestamp
    dayDungeonFailStatMap["dungeonType"] = key
    dayDungeonFailStatMap["dungeonFailNum"] = value
    for key, value in dungeonFailStarsStat[key].items():
        dayDungeonFailStatMap["failStar" + key] = value
dungeon_fail_stat_file = open(dungeon_fail_stat_path, 'a')
try:
    dungeon_fail_stat_file.write(("{'message':" + json.dumps(dayDungeonFailStatMap) + "}").replace("'", "\"") + "\n")
finally:
    dungeon_fail_stat_file.close()


# output card operate num into middle log file
card_operate_file = open(user_operation_midfile_path, 'a')
try:
    for key, value in userOperationNumDic.items():
        card_operate_file.write("{\"" + str(key) + "\":" + str(value) + "}\n")
finally:
    card_operate_file.close()

