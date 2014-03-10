#!/usr/bin/python
import json
import MySQLdb
import time
# init var of base
gameCode = "pokersg"
serverId = "1001"
regionId = "1"
timestamp = str(long(time.time() * 1000))
#init file path
vipLv_stat_path = "E:/work/workspace/sgpoker/logs/stat/vip_stat.log"
#init db
db_ip = "127.0.0.1"
db_user = "root"
db_pwd = ""
db_db = "sg2"
db_port = 3306
# global attribute
totalVip = 0
vipLvMap = {}

try:
    conn = MySQLdb.connect(host=db_ip, user=db_user, passwd=db_pwd, db=db_db, port=db_port)
    cur = conn.cursor()
    cur.execute('select count(1) from role_info where vipLv>0')
    result = cur.fetchone()
    totalVip = result[0]
    cur.execute('select count(1),vipLv from role_info group by vipLv')
    result = cur.fetchall()
    for r in result:
        vipLvMap["vip" + str(r[1])] = r[0]
    #add vipLvMap params
    vipLvMap["totalVip"] = totalVip
    vipLvMap["gameCode"] = gameCode
    vipLvMap["serverId"] = serverId
    vipLvMap["regionId"] = regionId
    vipLvMap["timestamp"] = timestamp
    cur.close()
    conn.close()
except MySQLdb.Error, e:
    print "Mysql Error %d: %s" % (e.args[0], e.args[1])

vipoutput = open(vipLv_stat_path, 'a')
try:
    vipoutput.write(("{'message':" + json.dumps(vipLvMap) + "}").replace("'", "\"") + "\n")
finally:
    vipoutput.close()