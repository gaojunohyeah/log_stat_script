#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import MySQLdb
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
# 数据库参数
db_ip = "127.0.0.1"
db_user = "root"
db_pwd = ""
db_db = "sgpoker"
db_port = 3306
# elasticsearch 连接参数
es_host = 'localhost'
index_name = 'stat_log-' + time.strftime("%Y.%m", )
statType = {
    'FINANCIAL_STAT': 'financial_stat',
    'COMSUME_POINT_STAT': 'consume_point_stat'
}
doc = {
    'message': {
    },
    '@timestamp': timestamp,
    'type': ''
}
# 文件路径
# jade_log_path = "E:/work/workspace/sgpoker/logs/stat/jade_log.log"
jade_log_path = "/data/game_server/logs/stat/jade_log.log"
# finalcial_stat_path = "E:/work/workspace/sgpoker/logs/stat/financial_stat.log"
# consume_point_stat_path = "E:/work/workspace/sgpoker/logs/stat/consume_point_stat.log"
# 玉石日志 原因字典
# 获取玉石字典
jadeLogReasonDic_Gain = {'JADE_GAIN_MDDR': 401,
                         'JADE_GAIN_LB': 402,
                         'JADE_CREATE_ROLE': 403,
                         'JADE_COL': 404,
                         'JADE_DUNGEON': 405,
                         'JADE_GAIN_GM': 411,
                         'JADE_CHARGE_GIFT': 414
}
# 消耗玉石字典
jadeLogReasonDic_Consume = {'JADE_GACHA': 406,
                            'JADE_ACTB': 407,
                            'JADE_CARD_NUM': 408,
                            'JADE_COST': 409,
                            'JADE_BUQIAN': 410,
                            'JADE_RAISED': 412,
                            'JADE_LVLLIMIT': 413
}
# 全局变量
sum = 0
consume_money = 0
consumeRMB = 0
new_charge = 0
chargelist = set()
consumelist = set()
totalgmStone = ""
totalStone = ""

consumePointStatDic = {}
consumePersonDic = {}

# 进行玉石日志统计
def jadelogtojson(line):
    #print line
    global sum
    global chargelist
    global consume_money
    global consumeRMB
    global new_charge
    s = json.loads(line)
    # 获取玉石的日志类型
    if s["message"]["reason"] == jadeLogReasonDic_Gain.get('JADE_GAIN_MDDR'):
        chargelist.add(s["message"]["charId"])
        sum += s["message"]["useJade"]
        #print s["message"]["charId"]
        if s["message"]["param"].split(";")[1] == 0:
            new_charge += 1
    # 消耗玉石的日志类型
    if s["message"]["reason"] in jadeLogReasonDic_Consume.values():
        #print s["message"]["charId"]
        if s["message"]["jadetype"] == 1:
            consume_money += s["message"]["useJade"]
        elif s["message"]["jadetype"] == 2:
            consumeRMB += s["message"]["useJade"]
        consumelist.add(s["message"]["charId"])

        # 进行每日玉石消耗统计
        reason = s["message"]["reason"]
        # 如果没有该日志原因的对象，则实例化一个并添加统计计数
        if (not consumePointStatDic.has_key(reason)):
            consumePointStatDic[reason] = ConsumePointStatBean(gameCode, serverId, regionId, timestamp, reason, 0, 0, 0)
        if (not consumePersonDic.has_key(reason)):
            consumePersonDic[reason] = set()
        consumePointStatDic[reason].consumeTimesNum += 1
        consumePointStatDic[reason].consumeJadeNum += s["message"]["useJade"]
        consumePersonDic[reason].add(s["message"]["charId"])


try:
    conn = MySQLdb.connect(host=db_ip, user=db_user, passwd=db_pwd, db=db_db, port=db_port)
    cur = conn.cursor()
    # 获取全服的GM玉石和RMB玉石留存总量
    cur.execute('select sum(gmStone) as totalgmStone,sum(stone) as totalStone from role_info')
    result = cur.fetchone()
    totalgmStone = result[0]
    totalStone = result[1]
    if (None == totalgmStone):
        totalgmStone = 0
    if (None == totalStone):
        totalStone = 0
    cur.close()
    conn.close()
except MySQLdb.Error, e:
    print "Mysql Error %d: %s" % (e.args[0], e.args[1])

#print "gamecode:"+gamecode
#print "serverId:"+serverId
#print "sum:"+str(sum)
#print "consume_money:"+str(-consume_money)
#print "charge:"+str(len(chargelist))
#print "consume:"+str(len(consumelist))
#print "arpu:"+str(sum/len(chargelist))


# 定义统计对象
# FinancialStatBean
class FinancialStatBean(object):
    def __init__(self, gameCode, serverId, regionId, consume_money, new_charge, totalChargeUser, totalConsumeUser,
                 totalgmStone, totalStone, totalRechargeStone, arpu, timestamp, consumeRMB):
        self.gameCode = gameCode
        self.serverId = serverId
        self.regionId = regionId
        self.consumeMoney = consume_money
        self.newCharge = new_charge
        self.totalChargeUser = totalChargeUser
        self.totalConsumeUser = totalConsumeUser
        self.totalgmStone = totalgmStone
        self.totalStone = totalStone
        self.totalRechargeStone = totalRechargeStone
        self.arpu = arpu
        self.timestamp = timestamp
        #self.totalVip=totalVip
        self.consumeRMB = consumeRMB
        #def __repr__(self):
        #	return 'FinancialStatBean Object gamecode : %s , serverId : %s' % (self.gamecode,self.serverId)


# 定义统计对象
# ConsumePointStatBean
class ConsumePointStatBean(object):
    def __init__(self, gameCode, serverId, regionId, timestamp, reason, consumePeopleNum, consumeTimesNum,
                 consumeJadeNum):
        self.gameCode = gameCode
        self.serverId = serverId
        self.regionId = regionId
        self.timestamp = timestamp
        self.reason = reason
        self.consumePeopleNum = consumePeopleNum
        self.consumeTimesNum = consumeTimesNum
        self.consumeJadeNum = consumeJadeNum

# 将object对象转换为字典
def object2dict(obj):
    d = {}
    #d["__class__"] = obj.__class__.__name__
    #d["__module__"] = obj.__module__
    d.update(obj.__dict__)
    return d

# 是否存在昨天的日志文件，如果没有，则读取目前的日志文件
if os.path.exists(jade_log_path + yestodayLogName):
    jade_log_path += yestodayLogName
# 读取玉石日志文件开始进行玉石日志统计
for line in open(jade_log_path):
    jadelogtojson(line, )

# f = FinancialStatBean
# if (0 == len(chargelist)):
#     f = FinancialStatBean(gameCode, serverId, regionId, -consume_money, new_charge, len(chargelist), len(consumelist),
#                           str(totalgmStone), str(totalStone), sum, sum, timestamp, -consumeRMB)
# else:
#     f = FinancialStatBean(gameCode, serverId, regionId, -consume_money, new_charge, len(chargelist), len(consumelist),
#                           str(totalgmStone), str(totalStone), sum, sum / len(chargelist), timestamp, -consumeRMB)
# d = object2dict(f)
#
# finalcial_stat_file = open(finalcial_stat_path, 'a')
#
# try:
#     finalcial_stat_file.write(("{'message':" + str(d) + "}").replace("'", "\"") + "\n")
# finally:
#     finalcial_stat_file.close()


# # output consume point stat file
# consume_point_stat_file = open(consume_point_stat_path, 'a')
#
# try:
#     for key, value in consumePointStatDic.items():
#         obj = consumePointStatDic.get(key)
#         obj.consumePeopleNum = len(consumePersonDic.get(key))
#         obj.consumeJadeNum = -obj.consumeJadeNum
#         dic = object2dict(obj)
#         consume_point_stat_file.write(("{'message':" + str(dic) + "}").replace("'", "\"") + "\n")
# finally:
#     consume_point_stat_file.close()


# 初始化ES连接
es = Elasticsearch([
    {'host': es_host},
    ])


# 封装每日收入统计对象
f = FinancialStatBean
if (0 == len(chargelist)):
    f = FinancialStatBean(gameCode, serverId, regionId, -consume_money, new_charge, len(chargelist), len(consumelist),
                          str(totalgmStone), str(totalStone), sum, sum, timestamp, -consumeRMB)
else:
    f = FinancialStatBean(gameCode, serverId, regionId, -consume_money, new_charge, len(chargelist), len(consumelist),
                          str(totalgmStone), str(totalStone), sum, sum / len(chargelist), timestamp, -consumeRMB)

doc['type'] = statType['FINANCIAL_STAT']
doc['message'] = object2dict(f)
# 向ES中put统计数据
res = es.index(index=index_name, doc_type=doc['type'], id=uuid.uuid1(), body=doc)
if (not res['ok']):
    print "Elasticsearch put Error : timestamp->%s index->%s type->%s doc->%s" % (
        time.strftime("%Y-%m-%d %H:%M:%S", ), index_name, statType, doc)


# 封装每日玉石消费点统计对象
doc['type'] = statType['COMSUME_POINT_STAT']
doc['message'] = {}
# 向ES中put统计数据
for key, value in consumePointStatDic.items():
    obj = value
    obj.consumePeopleNum = len(consumePersonDic.get(key))
    obj.consumeJadeNum = -obj.consumeJadeNum
    doc['message'] = object2dict(obj)
    res = es.index(index=index_name, doc_type=doc['type'], id=uuid.uuid1(), body=doc)
    if (not res['ok']):
        print "Elasticsearch put Error : timestamp->%s index->%s type->%s doc->%s" % (
            time.strftime("%Y-%m-%d %H:%M:%S", ), index_name, statType, doc)

