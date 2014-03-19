#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
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
# elasticsearch 连接参数
es_host = 'localhost'
index_name = 'stat_log-' + time.strftime("%Y.%m", )
statType = {
    'USER_OPERATION_STAT': 'user_operation_stat'
}
doc = {
    'message': {
    },
    '@timestamp': timestamp,
    'type': ''
}
# 文件路径
# user_operation_stat_path = "E:/work/workspace/sgpoker/logs/stat/user_operation_stat.log"
# user_operation_midfile_path = "E:/work/workspace/sgpoker/logs/stat/user_operate_midfile.log"
user_operation_midfile_path = "/data/game_server/logs/stat/user_operate_midfile.log"
# 全局变量
userOperationStatList = []
userOperationStatMap = {}


# 定义统计对象
# UserOperationStatBean
class UserOperationStatBean(object):
    def __init__(self, gameCode, serverId, regionId, timestamp, userOperation, userOperationNum):
        self.gameCode = gameCode
        self.serverId = serverId
        self.regionId = regionId
        self.timestamp = timestamp
        self.userOperation = userOperation
        self.userOperationNum = userOperationNum


# 将object对象转换为字典
def object2dict(obj):
    d = {}
    #d["__class__"] = obj.__class__.__name__
    #d["__module__"] = obj.__module__
    d.update(obj.__dict__)
    return d


# # output scard_source_stat into log file
# userOperationStatMap["gameCode"] = gameCode
# userOperationStatMap["serverId"] = serverId
# userOperationStatMap["regionId"] = regionId
# userOperationStatMap["timestamp"] = timestamp

# 读取用户操作中间文件，进行数据整合
user_operation_midfile_file = open(user_operation_midfile_path, 'r+')
for line in user_operation_midfile_file:
    jsonline = json.loads(line)
    for key in jsonline.keys():
        # 添加统计对象至list中，统一进行ES的put操作
        user_operation_stat_object = UserOperationStatBean(gameCode, serverId, regionId, timestamp, key, jsonline[key])
        userOperationStatList.append(user_operation_stat_object)
        # userOperationStatMap[key] = jsonline[key]

# # output card operate num into middle log file
# user_operation_file = open(user_operation_stat_path, 'a')
# try:
#     user_operation_file.write(("{'message':" + json.dumps(userOperationStatMap) + "}").replace("'", "\"") + "\n")
#     # truncate the user_operation_midfile_file
#     user_operation_midfile_file.truncate(0)
# finally:
#     user_operation_file.close()

# 初始化ES连接
es = Elasticsearch([
    {'host': es_host},
])


# 向ES中put统计数据
doc['type'] = statType['USER_OPERATION_STAT']
for elem in userOperationStatList:
    doc['message'] = object2dict(elem)
    res = es.index(index=index_name, doc_type=doc['type'], id=uuid.uuid1(), body=doc)
    if (not res['ok']):
        print "Elasticsearch put Error : timestamp->%s index->%s type->%s doc->%s" % (
            time.strftime("%Y-%m-%d %H:%M:%S", ), index_name, statType, doc)

user_operation_midfile_file.truncate(0)