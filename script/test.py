#!/usr/bin/python
# -*- coding:utf-8 -*-
import xlrd
import datetime
import time
import os
import uuid
from elasticsearch import Elasticsearch
import sys
from dateutil import rrule
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
# doc = {
#     'author': 'kimchy',
#     'text': 'Elasticsearch: cool. bonsai cool.',
#     'message':{
#         'test':1,
#         'time':'adfsd'
#     },
#     'timestamp': str(long(time.time() * 1000))
# }
# res = es.index(index="test-index", doc_type='tweet', id=1, body=doc)
# print (res['ok'])
#
# res = es.exists(index="test-index", doc_type='tweet', id='2')
# print res
#
# res = es.mget(body={'ids':[1,2,3,4,5]},index="test-index", doc_type='tweet')
# for elem in res['docs']:
#     print elem['_id'],elem['exists'],elem['_source']

# res = es.get(index="test-index", doc_type='tweet', id='2')
# print (res['_source'])
#
#
# res = es.search(index="test-index", body={"query": {"match_all": {}}})
# print("Got %d Hits:" % res['hits']['total'])
# for hit in res['hits']['hits']:
#     print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])
#
# print 'ok'

# print "Elasticsearch put Error : doc->%s" % (doc)
#
# print datetime
#
# print time.strftime("%Y-%m",)
#
# print time.strftime("%Y-%m-%d %H:%M:%S",)

# statType = [1,2,3,4,5]
#
# print statType.index(5)

# print sys.argv[0]
# print sys.argv[1]
# print sys.argv[2]

# todayZero = long(time.mktime(datetime.date.today().timetuple()) * 1000)
# print long(time.time()*1000)
# print todayZero

# d1 = datetime.datetime(2005, 2, 16)
# d2 = datetime.datetime(2004, 12, 31)
# print (d1 - d2).days
#
# starttime = datetime.datetime.fromtimestamp(int(1395368949982/1000))
# endtime = datetime.datetime.fromtimestamp(int(1395369949982/1000))
# print starttime
# print endtime
# print (endtime - starttime).seconds
#
#
# hours = rrule.rrule(rrule.HOURLY, dtstart=starttime, until=endtime)
# days = rrule.rrule(rrule.DAILY, dtstart=starttime, until=endtime)
# print days.count()
# print hours.count()


# now = datetime.date.today()
# d = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
# t = long(time.mktime(d.timetuple()) * 1000 - 1)
#
#
# print t



# import json
# jade_log_path = "/data/game_server/logs/stat/jade_log.log"
# for line in open(jade_log_path):
#     s = json.loads(line)
#     if s["message"]["jadeType"] == 2:
#         print  s["message"]["reason"],s["message"]["useJade"]


search_doc = {
    "query": {
        "filtered": {
            "query": {
                "bool": {
                    "should": [
                        {
                            "query_string": {
                                "query": "type:\"financial_stat\" AND message.gameCode:pokersg"
                            }
                        }
                    ]
                }
            },
            "filter": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "@timestamp": {
                                    "from": 1401863667848,
                                    "to": 1401950067848
                                }
                            }
                        }
                    ]
                }
            }
        }
    },
    "size": 100000
}


res = es.search(index="test-index", body=search_doc)
print("Got %d Hits:" % res['hits']['total'])
for hit in res['hits']['hits']:
    print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])