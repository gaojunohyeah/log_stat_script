#!/usr/bin/python
import json
import MySQLdb
import os
from datetime import *
import time
#init var of method
sum=0
gameCode="pokersg"
serverId="1001"
regionId="1"
consume_money=0
consumeRMB=0
new_charge=0
chargelist = set()
consumelist = set()
totalgmStone=""
totalStone=""
totalVip=0
timestamp=str(long(time.time()*1000))
#init file path
finalcial_log_path="E:/work/workspace/sgpoker/logs/jade_log.log"
finalcial_stat_path="E:/work/workspace/sgpoker/logs/stat/financial_stat.log"
vipLv_stat_path="E:/work/workspace/sgpoker/logs/stat/vip_stat.log"
#init db
db_ip="127.0.0.1"
db_user="root"
db_pwd=""
db_db="sg2"
db_port=3306

vipLvMap={}
def jadelogtojson(line):
    #print line
    global sum
    global chargelist
    global consume_money
    global consumeRMB
    s = json.loads(line)
    #print s["message"]["reason"] < 409
    if s["message"]["reason"] == 401:
        chargelist.add(s["message"]["charId"])
        sum+=s["message"]["useJade"]
        #print s["message"]["charId"]
        if s["message"]["param"].split(";")[1] == 0:
            new_charge+=1
    if s["message"]["reason"] >= 406 and s["message"]["reason"] <= 413:
        #print s["message"]["charId"]
        if s["message"]["jadetype"] == 1:
            consume_money+=s["message"]["useJade"]
        elif s["message"]["jadetype"] == 2:
            consumeRMB+=s["message"]["useJade"]
        consumelist.add(s["message"]["charId"])
for line in open(finalcial_log_path):
    jadelogtojson(line,)


#print "gamecode:"+gamecode
#print "serverId:"+serverId
#print "sum:"+str(sum)
#print "consume_money:"+str(-consume_money)
#print "charge:"+str(len(chargelist))
#print "consume:"+str(len(consumelist))
#print "arpu:"+str(sum/len(chargelist))

try:
    conn=MySQLdb.connect(host=db_ip,user=db_user,passwd=db_pwd,db=db_db,port=db_port)
    cur=conn.cursor()
    cur.execute('select sum(gmStone) as totalgmStone,sum(stone) as totalStone from role_info')
    result =  cur.fetchone()
    totalgmStone = result[0]
    totalStone = result[1]
    cur.execute('select count(1) from role_info where vipLv>0')
    result = cur.fetchone()
    totalVip=result[0]
    cur.execute('select count(1),vipLv from role_info group by vipLv')
    result =  cur.fetchall()
    for r in result:
        vipLvMap["vip"+str(r[1])]=r[0]
    #add vipLvMap params
    vipLvMap["totalVip"]=totalVip
    vipLvMap["gameCode"]=gamecode
    vipLvMap["serverId"]=serverId
    vipLvMap["regionId"]=regionId
    vipLvMap["timestamp"]=timestamp
    cur.close()
    conn.close()
except MySQLdb.Error,e:
     print "Mysql Error %d: %s" % (e.args[0], e.args[1])
class FinancialStatBean(object):
        def __init__(self,gameCode,serverId,regionId,consume_money,new_charge,totalChargeUser,totalConsumeUser,totalgmStone,totalStone,totalRechargeStone,arpu,timestamp,consumeRMB):
            self.gameCode=gameCode
            self.serverId=serverId
            self.regionId=regionId
            self.consumeMoney=consume_money
            self.newCharge=new_charge
            self.totalChargeUser=totalChargeUser
            self.totalConsumeUser=totalConsumeUser
            self.totalgmStone=totalgmStone
            self.totalStone=totalStone
            self.totalRechargeStone=totalRechargeStone
            self.arpu=arpu
            self.timestamp=timestamp
            #self.totalVip=totalVip
            self.consumeRMB=consumeRMB
        #def __repr__(self):
        #	return 'FinancialStatBean Object gamecode : %s , serverId : %s' % (self.gamecode,self.serverId)
def object2dict(obj):
    d = {}
    #d["__class__"] = obj.__class__.__name__
    #d["__module__"] = obj.__module__
    d.update(obj.__dict__)
    return d
f=FinancialStatBean(gameCode,serverId,regionId,-consume_money,new_charge,len(chargelist),len(consumelist),str(totalgmStone),str(totalStone),sum,sum/len(chargelist),timestamp,consumeRMB)
d = object2dict(f)

output = open(finalcial_stat_path, 'a')

try:
    output.write(("{'message':"+str(d)+"}").replace("'","\"")+"\n")
finally:
    output.close()
vipoutput = open(vipLv_stat_path, 'a')
try:
    vipoutput.write(("{'message':"+json.dumps(vipLvMap)+"}").replace("'","\"")+"\n")
finally:
    output.close()

