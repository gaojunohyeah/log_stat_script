#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import time
import datetime
import os
import sys
import uuid
from elasticsearch import Elasticsearch
# init var of base
timestamp = str(long(time.time() * 1000))
yestoday = str(datetime.date.today() - datetime.timedelta(days=1))
if (len(sys.argv) == 2):
    yestoday = str(sys.argv[1])
yestodayLogName = "." + yestoday + ".log"
# elasticsearch 连接参数
es_host = 'localhost'
index_name = 'stat_log-' + time.strftime("%Y.%m", )
statType = {
    'RECHARGE_STAT': 'recharge_stat'
}
doc = {
    'message': {
    },
    '@timestamp': timestamp,
    'type': ''
}
#init file path
# recharge_log_path = "E:/work/workspace/sgpoker/logs/stat/recharge"
recharge_log_path = "/data/app/tomcat2/logs/passport/recharge"
# recharge_log_result_path = "/data/app/tomcat2/logs/passport/recharge_statistics_log"
# global attribute

rechargeMap = {}


def rechargelogtojson(line):
    s = json.loads(line)
    gameCode = str(s["message"]["gameCode"])
    regionId = str(s["message"]["regionId"])
    serverId = str(s["message"]["serverId"])
    userId = s["message"]["userId"]
    key = gameCode, regionId, serverId, str(userId)
    rechargeType = str(s["message"]["rechargeType"])
    creditAmount = float(s["message"]["creditAmount"])
    timestamp = long(s["message"]["timestamp"])
    #registerTimestamp = long(s["message"]["registerTimestamp"])
    if (not s["message"].has_key("registerTimestamp")):
        registerTimestamp = long(0)
    else:
        registerTimestamp = long(s["message"]["registerTimestamp"])
    if (not s["message"].has_key("lastLoginTimestamp")):
        lastLoginTimestamp = long(0)
    else:
        lastLoginTimestamp = long(s["message"]["lastLoginTimestamp"])
    # if stat info has this reason's info, if not, init one.
    if (not rechargeMap.has_key(key)):
        rechargeMap[key] = RechargeStatBean(gameCode, serverId, regionId, userId, rechargeType, creditAmount, 1,
                                            timestamp, timestamp, str(registerTimestamp), str(lastLoginTimestamp), timestamp)
    else:
        rechargeMap[key].totalCreditAmount += creditAmount
        rechargeMap[key].totalRechargeCnt += 1
        if (rechargeMap[key].lastRechargeTimestamp < timestamp):
            rechargeMap[key].lastRechargeTimestamp = timestamp


class RechargeStatBean(object):
    def __init__(self, gameCode, serverId, regionId, accountId, rechargeType, totalCreditAmount, totalRechargeCnt,
                 firstRechargeTimestamp, lastRechargeTimestamp, registerTimestamp, lastLoginTimestamp, timestamp):
        self.gameCode = gameCode
        self.serverId = serverId
        self.regionId = regionId
        self.accountId = accountId
        self.rechargeType = rechargeType
        self.totalCreditAmount = totalCreditAmount
        self.totalRechargeCnt = totalRechargeCnt
        self.firstRechargeTimestamp = firstRechargeTimestamp
        self.lastRechargeTimestamp = lastRechargeTimestamp
        self.registerTimestamp = registerTimestamp
        self.lastLoginTimestamp = lastLoginTimestamp
        self.timestamp = timestamp


def object2dict(obj):
    d = {}
    #d["__class__"] = obj.__class__.__name__
    #d["__module__"] = obj.__module__
    d.update(obj.__dict__)
    return d


if os.path.exists(recharge_log_path + yestodayLogName):
    recharge_log_path += yestodayLogName
for line in open(recharge_log_path):
    if (line != '\n'):
        rechargelogtojson(line)

# recharge_stat_file = open(recharge_log_result_path, 'a')
# try:
#     for k in rechargeMap:
#         d = object2dict(rechargeMap[k])
#         recharge_stat_file.write(("{'message':" + str(d) + "}").replace("'", "\"") + "\n")
#
# finally:
#     recharge_stat_file.close()


# 初始化ES连接
es = Elasticsearch([
    {'host': es_host},
    ])

# 封装每日充值统计对象
doc['type'] = statType['RECHARGE_STAT']
doc['message'] = {}
# 向ES中put统计数据
for k in rechargeMap:
    doc['message'] = object2dict(rechargeMap[k])
    res = es.index(index=index_name, doc_type=doc['type'], id=uuid.uuid1(), body=doc)
    if (not res['ok']):
        print "Elasticsearch put Error : timestamp->%s index->%s type->%s doc->%s" % (
            time.strftime("%Y-%m-%d %H:%M:%S", ), index_name, statType, doc)
