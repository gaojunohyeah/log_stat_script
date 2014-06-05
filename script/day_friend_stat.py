#!/usr/bin/python
# -*- coding:utf-8 -*-
import MySQLdb
import time
import datetime
import uuid
from elasticsearch import Elasticsearch
import sys
# init var of base
gameCode = "pokersg"
serverId = "1001"
regionId = "1"
now = datetime.date.today()
d = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
timestamp = str(long(time.mktime(d.timetuple()) * 1000 - 1))
if (len(sys.argv) == 5):
    gameCode = str(sys.argv[1])
    regionId = str(sys.argv[2])
    serverId = str(sys.argv[3])
    timestamp = str(sys.argv[4])
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
    'FRIEND_NUM_STAT': 'friend_num_stat'
}
doc = {
    'message': {
    },
    '@timestamp': timestamp,
    'type': ''
}
# 其他静态常量
friendNumLabelArea = [[0, 4], [5, 10], [11, 20], [20, 30], [31, 10000]]
# 全局变量
friendStatDic = {0: ['ZERO_TO_FOUR', set()],
                 1: ['FIVE_TO_TEN', set()],
                 2: ['ELEVEN_TO_TWENTY', set()],
                 3: ['TWENTYONE_TO_THIRTY', set()],
                 4: ['OVER_THIRTY', set()]
}
friendNumDic = {}


# 定义统计对象
# FriendStatBean
class FriendStatBean(object):
    def __init__(self, gameCode, serverId, regionId, timestamp, friendNumArea, peopleNum):
        self.gameCode = gameCode
        self.serverId = serverId
        self.regionId = regionId
        self.timestamp = timestamp
        self.friendNumArea = friendNumArea
        self.peopleNum = peopleNum


# 将object对象转换为字典
def object2dict(obj):
    d = {}
    #d["__class__"] = obj.__class__.__name__
    #d["__module__"] = obj.__module__
    d.update(obj.__dict__)
    return d


# 在数据库进行好友数量信息查询
def doFriendSearch():
    try:
        conn = MySQLdb.connect(host=db_ip, user=db_user, passwd=db_pwd, db=db_db, port=db_port)
        cur = conn.cursor()
        # 获取好友统计

        cur.execute(
            'select count(*) countNum,ri.id charId from rolefriendrelation rf,role_info ri where rf.roleid=ri.id group by ri.id;')
        result = cur.fetchall()
        # 将查询结果放置到字典中
        for r in result:
            friendNumDic[r[1]] = int(r[0])

        cur.execute(
            'select count(*) countNum,ri.id charId from rolefriendrelation rf,role_info ri where rf.friendid=ri.id group by ri.id;')
        result = cur.fetchall()
        # 判断字典中是否已经有该玩家的记录，如果有，则累加，如果没有，则直接赋值
        for r in result:
            if (not friendNumDic.has_key(r[1])):
                friendNumDic[r[1]] = int(r[0])
            else:
                friendNumDic[r[1]] += int(r[0])

        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


# 进行好友数量统计
def doFriendStat():
    # 循环好友数量字典
    for key, value in friendNumDic.items():
        # 判断该用户的好友数量所在的区间并统计
        for i in range(0, len(friendNumLabelArea), 1):
            if (value >= friendNumLabelArea[i][0] and value <= friendNumLabelArea[i][1]):
                friendStatDic[i][1].add(key)



doFriendSearch()

doFriendStat()

# 初始化ES连接
es = Elasticsearch([
    {'host': es_host},
    ])

# 封装每日好友数量统计对象
doc['type'] = statType['FRIEND_NUM_STAT']
doc['message'] = {}
# 向ES中put统计数据
for key,value in friendStatDic.items():
    obj = FriendStatBean(gameCode, serverId, regionId, timestamp, value[0], len(value[1]))
    doc['message'] = object2dict(obj)
    res = es.index(index=index_name, doc_type=doc['type'], id=uuid.uuid1(), body=doc)
    if (not res['ok']):
        print "Elasticsearch put Error : timestamp->%s index->%s type->%s doc->%s" % (
            time.strftime("%Y-%m-%d %H:%M:%S", ), index_name, statType, doc)