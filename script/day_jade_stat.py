#!/usr/bin/python
import json
import MySQLdb
import time
import datetime
import os
# init var of base
gameCode = "pokersg"
serverId = "1001"
regionId = "1"
timestamp = str(long(time.time() * 1000))
yestodayLogName = "." + str(datetime.date.today() - datetime.timedelta(days=1)) + ".log"
#init db
db_ip = "127.0.0.1"
db_user = "root"
db_pwd = ""
db_db = "sg2"
db_port = 3306
#init file path
jade_log_path = "E:/work/workspace/sgpoker/logs/stat/jade_log.log"
finalcial_stat_path = "E:/work/workspace/sgpoker/logs/stat/financial_stat.log"
consume_point_stat_path = "E:/work/workspace/sgpoker/logs/stat/consume_point_stat.log"
# jade_log reason dictionary
jadeLogReasonDic_Gain = {'JADE_GAIN_MDDR': 401,
                         'JADE_GAIN_LB': 402,
                         'JADE_CREATE_ROLE': 403,
                         'JADE_COL': 404,
                         'JADE_DUNGEON': 405,
                         'JADE_GAIN_GM': 411,
                         'JADE_CHARGE_GIFT': 414}

jadeLogReasonDic_Consume = {'JADE_GACHA': 406,
                            'JADE_ACTB': 407,
                            'JADE_CARD_NUM': 408,
                            'JADE_COST': 409,
                            'JADE_BUQIAN': 410,
                            'JADE_RAISED': 412,
                            'JADE_LVLLIMIT': 413}
# global attribute
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


def jadelogtojson(line):
    #print line
    global sum
    global chargelist
    global consume_money
    global consumeRMB
    global new_charge
    s = json.loads(line)
    #print s["message"]["reason"] < 409
    if s["message"]["reason"] == jadeLogReasonDic_Gain.get('JADE_GAIN_MDDR'):
        chargelist.add(s["message"]["charId"])
        sum += s["message"]["useJade"]
        #print s["message"]["charId"]
        if s["message"]["param"].split(";")[1] == 0:
            new_charge += 1
    if s["message"]["reason"] in jadeLogReasonDic_Consume.values():
        #print s["message"]["charId"]
        if s["message"]["jadetype"] == 1:
            consume_money += s["message"]["useJade"]
        elif s["message"]["jadetype"] == 2:
            consumeRMB += s["message"]["useJade"]
        consumelist.add(s["message"]["charId"])

        # do day jade reason stat
        reason = s["message"]["reason"]
        # if stat info has this reason's info, if not, init one.
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


class ConsumePointStatBean(object):
    def __init__(self, gameCode, serverId, regionId, timestamp, reasonId, consumePeopleNum, consumeTimesNum,
                 consumeJadeNum):
        self.gameCode = gameCode
        self.serverId = serverId
        self.regionId = regionId
        self.timestamp = timestamp
        self.reasonId = reasonId
        self.consumePeopleNum = consumePeopleNum
        self.consumeTimesNum = consumeTimesNum
        self.consumeJadeNum = consumeJadeNum


def object2dict(obj):
    d = {}
    #d["__class__"] = obj.__class__.__name__
    #d["__module__"] = obj.__module__
    d.update(obj.__dict__)
    return d


if os.path.exists(jade_log_path + yestodayLogName):
    jade_log_path += yestodayLogName

for line in open(jade_log_path):
    jadelogtojson(line, )

f = FinancialStatBean
if (0 == len(chargelist)):
    f = FinancialStatBean(gameCode, serverId, regionId, -consume_money, new_charge, len(chargelist), len(consumelist),
                          str(totalgmStone), str(totalStone), sum, sum, timestamp, -consumeRMB)
else:
    f = FinancialStatBean(gameCode, serverId, regionId, -consume_money, new_charge, len(chargelist), len(consumelist),
                          str(totalgmStone), str(totalStone), sum, sum / len(chargelist), timestamp, -consumeRMB)
d = object2dict(f)

finalcial_stat_file = open(finalcial_stat_path, 'a')

try:
    finalcial_stat_file.write(("{'message':" + str(d) + "}").replace("'", "\"") + "\n")
finally:
    finalcial_stat_file.close()


# output consume point stat file
consume_point_stat_file = open(consume_point_stat_path, 'a')

try:
    for key, value in consumePointStatDic.items():
        obj = consumePointStatDic.get(key)
        obj.consumePeopleNum = len(consumePersonDic.get(key))
        obj.consumeJadeNum = -obj.consumeJadeNum
        dic = object2dict(obj)
        consume_point_stat_file.write(("{'message':" + str(dic) + "}").replace("'", "\"") + "\n")
finally:
    consume_point_stat_file.close()
