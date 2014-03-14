#!/usr/bin/python
import json
import time
import datetime
import os
import sys
# init var of base
timestamp = str(long(time.time() * 1000))
yestoday = str(datetime.date.today() - datetime.timedelta(days=1))
if (len(sys.argv) == 2):
    yestoday = str(sys.argv[1])
yestodayLogName = "." + yestoday + ".log"
#init file path
recharge_log_path = "/data/app/tomcat2/logs/passport/recharge"
recharge_log_result_path = "/data/app/tomcat2/logs/passport/recharge_statistics_log"
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
                                            timestamp, timestamp, registerTimestamp, lastLoginTimestamp, yestoday)
    else:
        rechargeMap[key].totalCreditAmount += creditAmount
        rechargeMap[key].totalRechargeCnt += 1
        if (rechargeMap[key].lastRechargeTimestamp < timestamp):
            rechargeMap[key].lastRechargeTimestamp = timestamp


class RechargeStatBean(object):
    def __init__(self, gameCode, serverId, regionId, userId, rechargeType, totalCreditAmount, totalRechargeCnt,
                 firstRechargeTimestamp, lastRechargeTimestamp, registerTimestamp, lastLoginTimestamp, date):
        self.gameCode = gameCode
        self.serverId = serverId
        self.regionId = regionId
        self.userId = userId
        self.rechargeType = rechargeType
        self.totalCreditAmount = totalCreditAmount
        self.totalRechargeCnt = totalRechargeCnt
        self.firstRechargeTimestamp = firstRechargeTimestamp
        self.lastRechargeTimestamp = lastRechargeTimestamp
        self.registerTimestamp = registerTimestamp
        self.lastLoginTimestamp = lastLoginTimestamp
        self.date = date


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

recharge_stat_file = open(recharge_log_result_path, 'a')
try:
    for k in rechargeMap:
        d = object2dict(rechargeMap[k])
        recharge_stat_file.write(("{'message':" + str(d) + "}").replace("'", "\"") + "\n")

finally:
    recharge_stat_file.close()
