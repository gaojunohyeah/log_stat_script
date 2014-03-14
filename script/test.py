#!/usr/bin/python
# -*- coding:utf-8 -*-
import xlrd
import datetime
import time
import os
import uuid
from elasticsearch import Elasticsearch
# print datetime.date.today()
# st = "." + str(datetime.date.today() - datetime.timedelta(days=1)) + ".log"
# finalcial_log_path = "E:/work/workspace/sgpoker/logs/stat/jade_log.log"
# print st
# print finalcial_log_path, os.path.exists(finalcial_log_path)
# print finalcial_log_path + st, os.path.exists(finalcial_log_path + st)
# # gacha_excel_path = "E:/work/workspace/sgpoker_resources/config/common/gacha.xls"
# dungeon_excel_path = "E:/work/workspace/sgpoker_resources/config/common/dungeon.xls"
# stage_excel_path = "E:/work/workspace/sgpoker_resources/config/common/stage.xls"
#
# data = xlrd.open_workbook(dungeon_excel_path)
# table = data.sheets()[2]
# #
# types =  table.col_values(0)
# print types

# for i in range(0,5):
#     types.pop(0)
# types_names = table.col_values(1)
# print types_names
# for i in range(0,5):
#     types_names.pop(0)
#
#
# print len(types)
# #print types.
# print types_names
# #print types_names.count()

# a = set()
# friendNumLabelArea = [[0,4],[5,10],[11,20],[20,30],[31,10000]]
# for elem in friendNumLabelArea:
#     print friendNumLabelArea.index(elem)
#     print elem[0],elem[1]

# print uuid.uuid1()
#
# es = Elasticsearch([
#     {'host': 'localhost'},
#     ])
#
#
doc = {
    'author': 'kimchy',
    'text': 'Elasticsearch: cool. bonsai cool.',
    'message':{
        'test':1,
        'time':'adfsd'
    },
    'timestamp': str(long(time.time() * 1000))
}
# res = es.index(index="test-index", doc_type='tweet', id=1, body=doc)
# print (res['ok'])
#
# res = es.get(index="test-index", doc_type='tweet', id='1')
# print (res['_source'])
#
#
# res = es.search(index="test-index", body={"query": {"match_all": {}}})
# print("Got %d Hits:" % res['hits']['total'])
# for hit in res['hits']['hits']:
#     print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])
#
# print 'ok'

print "Elasticsearch put Error : doc->%s" % (doc)

print datetime

print time.strftime("%Y-%m",)

print time.strftime("%Y-%m-%d %H:%M:%S",)


