#!/usr/bin/python
import xlrd


cardLogReasonDic = {'JADE_GAIN_MDDR': 401,
                    'JADE_GAIN_LB': 402,
                    'JADE_CREATE_ROLE': 403,
                    'JADE_COL': 404,
                    'JADE_DUNGEON': 405,
                    'JADE_GACHA': 406,
                    'JADE_ACTB': 407,
                    'JADE_CARD_NUM': 408,
                    'JADE_COST': 409,
                    'JADE_BUQIAN': 410,
                    'JADE_GAIN_GM': 411,
                    'JADE_RAISED': 412,
                    'JADE_LVLLIMIT': 413,
                    'JADE_CHARGE_GIFT': 414}

#print len(cardLogReasonDic)

print (4007 in cardLogReasonDic.values())
# cardLogReasonDic["a"] =10
print cardLogReasonDic.has_key("a")

#print dir(list)

#print help(list)

# gacha_excel_path = "E:/work/workspace/sgpoker_resources/config/common/gacha.xls"
#
# data = xlrd.open_workbook(gacha_excel_path)
# table = data.sheets()[3]
#
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
