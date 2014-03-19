#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import MySQLdb
import time
import uuid
from elasticsearch import Elasticsearch
import sys
# 基础变量
gameCode = "pokersg"
serverId = "1001"
regionId = "1"
timestamp = str(long(time.time() * 1000))
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
    'VIP_STAT': 'vip_stat'
}
doc = {
    'message': {
    },
    '@timestamp': timestamp,
    'type': ''
}
# 文件路径
# vipLv_stat_path = "E:/work/workspace/sgpoker/logs/stat/vip_stat.log"
# 全局变量
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

# vipoutput = open(vipLv_stat_path, 'a')
# try:
#     vipoutput.write(("{'message':" + json.dumps(vipLvMap) + "}").replace("'", "\"") + "\n")
# finally:
#     vipoutput.close()

# 初始化ES连接
es = Elasticsearch([
    {'host': es_host},
])

# 封装VIP对象
doc['type'] = statType['VIP_STAT']
for key, value in vipLvMap.items():
    doc['message'][key] = value
# 向ES中put统计数据
res = es.index(index=index_name, doc_type=doc['type'], id=uuid.uuid1(), body=doc)
if (not res['ok']):
    print "Elasticsearch put Error : timestamp->%s index->%s type->%s doc->%s" % (
        time.strftime("%Y-%m-%d %H:%M:%S", ), index_name, statType, doc)

# res = es.get(index="test-index", doc_type='tweet', id='1')
# print (res['_source'])


