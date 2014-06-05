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
# elasticsearch 连接参数
es_host = 'localhost'
index_name = 'stat_log-' + time.strftime("%Y.%m", )
statType = {
    'SCARD_SOURCE_STAT': 'scard_source_stat',
    'SSCARD_ADD_STAT': 'sscard_add_stat'
}
doc = {
    'message': {
    },
    '@timestamp': timestamp,
    'type': ''
}
# 文件路径
# card_log_path = "E:/work/workspace/sgpoker/logs/stat/card_log.log"
card_log_path = "/data/game_server/logs/stat/card_log.log"

# sscard_add_stat_path = "E:/work/workspace/sgpoker/logs/stat/sscard_add_stat.log"
# scard_source_stat_path = "E:/work/workspace/sgpoker/logs/stat/scard_source_stat.log"
# user_operation_midfile_path = "E:/work/workspace/sgpoker/logs/stat/user_operate_midfile.log"
user_operation_midfile_path = "/data/game_server/logs/stat/user_operate_midfile.log"

# gacha_excel_path = "E:/work/workspace/sgpoker_resources/config/common/gacha.xls"
gacha_excel_path = "/data/resources/config/common/gacha.xls"
# 卡牌日志 原因字典
# 获取卡牌字典
cardLogReasonDic_Get = {'CARD_CREATE_ROLE': 201,  # 卡片获得_初次登录送普牌
                        'CARD_CREATE_ROLE_A': 202,  # 卡片获得_初次登录玩家选A牌
                        'CARD_BOSSDROP_ADD': 203,  # 卡片获得_怪物掉落
                        'CARD_GACHA_ADD': 204,  # 卡片获得_抽奖
                        'CARD_COMB_ADD': 205,  # 卡片获得_进化
                        'CARD_GIFT_ADD': 206,  # 卡片获得_礼包
                        'CARD_WEIXIN': 219,  # 卡牌获得_微信
                        'CARD_SAODANG': 220,  # 卡牌获得扫荡
                        'CARD_IMPOSE': 221,  # 卡牌获得强征
                        'CARD_QUEST': 222,  # 卡牌获得_每日/主线任务
                        'EQUIPMENT_QUEST': 223,  # 装备获得_每日/主线任务
                        'EQUIPMENT_DROP': 224,  # 掉落获得装备
                        'EQUIPMENT_COMBINE': 225,  # 合成装备
                        'EQUIPMENT_GIFT': 227,  # 礼包获得装备
                        'EQUIPMENT_GM': 228  # 后台发装备
}
# 消耗卡牌字典
cardLogReasonDic_Consume = {'CARD_HECHENG_CONSUME_DEL': 207,  # 卡片消耗_合成材料
                            'CARD_IMP_DEL': 208,  # 卡片消耗_进化卡
                            'CARD_IMP_CONSUME_DEL': 209,  # 卡片消耗_进化材料
                            'CARD_SELL_DEL': 210,  # 卡片消耗_出售
                            'CARD_GM': 218,  # 卡片删除_gm后台添加/删除
                            'EQUIPMENT_SELL': 226  # 出售装备
}
# 其他卡牌字典
cardLogReasonDic_Other = {'CARD_CHANGE': 211,  # 普通卡片替换
                          'CARD_A_CHANGE': 212,  # A卡片替换
                          'CARD_SONCARDON': 213,  # 子卡装备
                          'CARD_SONCARDOUT': 214,  # 子卡卸下
                          'CARD_GETXP': 215,  # 卡片经验_获得经验
                          'CARD_LVLUP': 216,  # 卡片升级
                          'CARD_SKILL_LVLUP': 217  # 卡片技能升级
}
# 其他静态常量
S_CARD_LABEL = 3
SS_CARD_LABEL = 4
gacha_type_dic = {}
# 全局变量
ssCardAddNum = 0
ssCardAddUser = set()
cardSourceNumDic = {}
gacha_types = []
gacha_types_names = []
scardSourceStatMap = {}
userOperationNumDic = {}

# 定义统计对象
# SSCardAddStatBean
class SSCardAddStatBean(object):
    def __init__(self, gameCode, serverId, regionId, ssCardAddNum, ssCardAddUserNum, timestamp):
        self.gameCode = gameCode
        self.serverId = serverId
        self.regionId = regionId
        self.ssCardAddNum = ssCardAddNum
        self.ssCardAddUserNum = ssCardAddUserNum
        self.timestamp = timestamp


# function : logtojson
# 读取文件行转换为json对象
def logtojson(line):
    s = json.loads(line)
    return s


# function : dayCardStat
# 统计卡牌日志
def dayCardStat(jsonLine):
    global ssCardAddNum

    # 必须是卡牌新增类型，才统计卡牌新增以及来源统计
    if jsonLine["message"]["reason"] in cardLogReasonDic_Get.values():
        # 统计每日SS卡新增数量
        # 卡牌类型需要是SS级别及以上
        if jsonLine["message"]["cardQuality"] >= SS_CARD_LABEL:
            ssCardAddNum += 1
            # 对获得SS卡的用户进行排重
            ssCardAddUser.add(jsonLine["message"]["charId"])

        # 统计每日S卡以上来源方式
        # 卡牌类型需要时S级别及以上
        if jsonLine["message"]["cardQuality"] >= S_CARD_LABEL:
            if (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_CREATE_ROLE")
                or jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_CREATE_ROLE_A")):
                if (cardSourceNumDic.has_key("CARD_CREATE_ROLE")):
                    cardSourceNumDic["CARD_CREATE_ROLE"] += 1
                else:
                    cardSourceNumDic["CARD_CREATE_ROLE"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_GIFT_ADD")):
                if (cardSourceNumDic.has_key("CARD_GIFT_ADD")):
                    cardSourceNumDic["CARD_GIFT_ADD"] += 1
                else:
                    cardSourceNumDic["CARD_GIFT_ADD"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_BOSSDROP_ADD")):
                if (cardSourceNumDic.has_key("CARD_BOSSDROP_ADD")):
                    cardSourceNumDic["CARD_BOSSDROP_ADD"] += 1
                else:
                    cardSourceNumDic["CARD_BOSSDROP_ADD"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_WEIXIN")):
                if (cardSourceNumDic.has_key("CARD_WEIXIN")):
                    cardSourceNumDic["CARD_WEIXIN"] += 1
                else:
                    cardSourceNumDic["CARD_WEIXIN"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_COMB_ADD")):
                if (cardSourceNumDic.has_key("CARD_COMB_ADD")):
                    cardSourceNumDic["CARD_COMB_ADD"] += 1
                else:
                    cardSourceNumDic["CARD_COMB_ADD"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_GACHA_ADD")):
                # index = gacha_types.index(jsonLine["message"]["blessCardType"])
                type_name = 'blessCardType_' + str(jsonLine["message"]["blessCardType"])
                if (cardSourceNumDic.has_key(type_name)):
                    cardSourceNumDic[type_name] += 1
                else:
                    cardSourceNumDic[type_name] = 1

    # 统计每日卡牌操作次数数据
    if jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_COMB_ADD"):
        if (userOperationNumDic.has_key("CARD_COMB_ADD")):
            userOperationNumDic["CARD_COMB_ADD"] += 1
        else:
            userOperationNumDic["CARD_COMB_ADD"] = 1
    elif jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_GACHA_ADD"):
        if (userOperationNumDic.has_key("CARD_GACHA_ADD")):
            userOperationNumDic["CARD_GACHA_ADD"] += 1
        else:
            userOperationNumDic["CARD_GACHA_ADD"] = 1
    elif jsonLine["message"]["reason"] == cardLogReasonDic_Consume.get("CARD_HECHENG_CONSUME_DEL"):
        if (userOperationNumDic.has_key("CARD_HECHENG_CONSUME_DEL")):
            userOperationNumDic["CARD_HECHENG_CONSUME_DEL"] += 1
        else:
            userOperationNumDic["CARD_HECHENG_CONSUME_DEL"] = 1
    elif jsonLine["message"]["reason"] == cardLogReasonDic_Other.get("CARD_CHANGE"):
        if (userOperationNumDic.has_key("CARD_CHANGE")):
            userOperationNumDic["CARD_CHANGE"] += 1
        else:
            userOperationNumDic["CARD_CHANGE"] = 1
    elif jsonLine["message"]["reason"] == cardLogReasonDic_Other.get("CARD_A_CHANGE"):
        if (userOperationNumDic.has_key("CARD_A_CHANGE")):
            userOperationNumDic["CARD_A_CHANGE"] += 1
        else:
            userOperationNumDic["CARD_A_CHANGE"] = 1


# 将object对象转换为字典
def object2dict(obj):
    d = {}
    #d["__class__"] = obj.__class__.__name__
    #d["__module__"] = obj.__module__
    d.update(obj.__dict__)
    return d


def loadGachaExcel():
    global gacha_types
    global gacha_types_names

    # 加载抽卡类型excel
    data = xlrd.open_workbook(gacha_excel_path)
    table = data.sheets()[3]

    # 读取抽卡类型信息
    types = table.col_values(0)
    for i in range(5, len(types), 1):
        gacha_types.append(int(types[i]))

    # 读取抽卡类型名称信息
    gacha_types_names = table.col_values(1)
    for i in range(0, 5, 1):
        gacha_types_names.pop(0)


# 加载抽卡excel配置信息
loadGachaExcel()

# 是否存在昨天的日志文件，如果没有，则读取目前的日志文件
if os.path.exists(card_log_path + yestodayLogName):
    card_log_path += yestodayLogName
# 读取卡牌日志文件开始进行卡牌日志统计
for line in open(card_log_path):
    jsonLine = logtojson(line, )
    # 统计卡牌日志
    dayCardStat(jsonLine)



# # output sscard_add_stat into log file
# sscard_add_stat_object = SSCardAddStatBean(gameCode, serverId, regionId, ssCardAddNum, len(ssCardAddUser), timestamp)
# sscard_add_stat_log = object2dict(sscard_add_stat_object)
# sscard_add_file = open(sscard_add_stat_path, 'a')
# try:
#     sscard_add_file.write(("{'message':" + str(sscard_add_stat_log) + "}").replace("'", "\"") + "\n")
# finally:
#     sscard_add_file.close()

# # output scard_source_stat into log file
# sscardSourceStatMap["gameCode"] = gameCode
# sscardSourceStatMap["serverId"] = serverId
# sscardSourceStatMap["regionId"] = regionId
# sscardSourceStatMap["timestamp"] = timestamp
# for key, value in cardSourceNumDic.items():
#     sscardSourceStatMap[key] = value
# scard_source_file = open(scard_source_stat_path, 'a')
# try:
#     scard_source_file.write(("{'message':" + json.dumps(sscardSourceStatMap) + "}").replace("'", "\"") + "\n")
# finally:
#     scard_source_file.close()


# 输出卡牌操作统计数据至用户操作中间文件
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

# 封装SS卡牌新增统计对象
doc['type'] = statType['SSCARD_ADD_STAT']
sscard_add_stat_object = SSCardAddStatBean(gameCode, serverId, regionId, ssCardAddNum, len(ssCardAddUser), timestamp)
doc['message'] = object2dict(sscard_add_stat_object)
# 向ES中put统计数据
res = es.index(index=index_name, doc_type=doc['type'], id=uuid.uuid1(), body=doc)
if (not res['ok']):
    print "Elasticsearch put Error : timestamp->%s index->%s type->%s doc->%s" % (
        time.strftime("%Y-%m-%d %H:%M:%S", ), index_name, statType, doc)


# 封装卡牌来源统计对象
scardSourceStatMap["gameCode"] = gameCode
scardSourceStatMap["serverId"] = serverId
scardSourceStatMap["regionId"] = regionId
scardSourceStatMap["timestamp"] = timestamp
for key, value in cardSourceNumDic.items():
    scardSourceStatMap[key] = value

doc['type'] = statType['SCARD_SOURCE_STAT']
doc['message'] = {}
for key, value in scardSourceStatMap.items():
    doc['message'][key] = value
# 向ES中put统计数据
res = es.index(index=index_name, doc_type=doc['type'], id=uuid.uuid1(), body=doc)
if (not res['ok']):
    print "Elasticsearch put Error : timestamp->%s index->%s type->%s doc->%s" % (
        time.strftime("%Y-%m-%d %H:%M:%S", ), index_name, statType, doc)




