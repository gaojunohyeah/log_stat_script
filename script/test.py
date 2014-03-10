#!/usr/bin/python
# -*- coding:utf-8 -*-
import xlrd
import datetime
import os

print datetime.date.today()
st = "." + str(datetime.date.today() - datetime.timedelta(days=1)) + ".log"
finalcial_log_path = "E:/work/workspace/sgpoker/logs/stat/jade_log.log"
print st
print finalcial_log_path, os.path.exists(finalcial_log_path)
print finalcial_log_path + st, os.path.exists(finalcial_log_path + st)
# gacha_excel_path = "E:/work/workspace/sgpoker_resources/config/common/gacha.xls"
dungeon_excel_path = "E:/work/workspace/sgpoker_resources/config/common/dungeon.xls"
stage_excel_path = "E:/work/workspace/sgpoker_resources/config/common/stage.xls"

data = xlrd.open_workbook(dungeon_excel_path)
table = data.sheets()[2]
#
types =  table.col_values(0)
print types
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
