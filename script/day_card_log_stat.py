#!/usr/bin/python
# -*- coding:utf-8 -*-
from bean.script_bean import *
import json
import xlrd
import time
# init var of method
gameCode = "pokersg"
serverId = "1001"
regionId = "1"
timestamp = str(long(time.time() * 1000))
# init file path
card_log_path = "E:/work/workspace/sgpoker/logs/stat/card_log.log"
sscard_add_stat_path = "E:/work/workspace/sgpoker/logs/stat/day/sscard_add_stat.log"
vipLv_stat_path = "E:/work/workspace/sgpoker/logs/stat/vip_stat.log"

gacha_excel_path = "E:/work/workspace/sgpoker_resources/config/common/gacha.xls"
# card_log reason dictionary
cardLogReasonDic_Get = {'CARD_CREATE_ROLE': 201,
                        'CARD_CREATE_ROLE_A': 202,
                        'CARD_BOSSDROP_ADD': 203,
                        'CARD_GACHA_ADD': 204,
                        'CARD_COMB_ADD': 205,
                        'CARD_GIFT_ADD': 206,
                        'CARD_WEIXIN': 219}

cardLogReasonDic_Consume = {'CARD_HECHENG_CONSUME_DEL': 207,
                            'CARD_IMP_DEL': 208,
                            'CARD_IMP_CONSUME_DEL': 209,
                            'CARD_SELL_DEL': 210,
                            'CARD_GM': 218}

cardLogReasonDic_Other = {'CARD_CHANGE': 211,
                          'CARD_A_CHANGE': 212,
                          'CARD_SONCARDON': 213,
                          'CARD_SONCARDOUT': 214,
                          'CARD_GETXP': 215,
                          'CARD_LVLUP': 216,
                          'CARD_SKILL_LVLUP': 217}
# other static constants
S_CARD_LABEL = 5
SS_CARD_LABEL = 7
gacha_type_dic = {}
# global attribute
ssCardAddNum = 0
ssCardAddUser = []
cardSourceNumDic = {}
gacha_types = []
gacha_types_names = []

# define stat object
# SSCardAddStatBean
class SSCardAddStatBean(object):
    def __init__(self, gameCode, serverId, regionId, ssCardAddNum, ssCardAddUserNum, timestamp):
        self.gameCode = gameCode
        self.serverId = serverId
        self.regionId = regionId
        self.ssCardAddNum = ssCardAddNum
        self.ssCardAddUserNum = ssCardAddUserNum
        self.timestamp = timestamp


# define stat object
# CardOperationStatBean
class CardOperationStatBean(object):
    def __init__(self, gameCode, serverId, regionId, ssCardAddNum, ssCardAddUserNum, timestamp):
        self.gameCode = gameCode
        self.serverId = serverId
        self.regionId = regionId
        self.ssCardAddNum = ssCardAddNum
        self.ssCardAddUserNum = ssCardAddUserNum
        self.timestamp = timestamp


# function ：cardlogtojson
# load card log file line to json object
def cardlogtojson(line):
    # print line
    s = json.loads(line)
    return s


# function ：dayCardStat
# stat card_log
def dayCardStat(jsonLine):
    global ssCardAddNum
    # global ssCardAddUser
    # # global cardSourceDic

    # should be the get card log, not consume card or other reason
    if jsonLine["message"]["reason"] in cardLogReasonDic_Get.values():
        # stat day sscard add num log
        # cardType should be sscard or even higher
        if jsonLine["message"]["cardQuality"] >= SS_CARD_LABEL:
            ssCardAddNum += 1
            # this user never get sscard before int today
            if ssCardAddUser.index(jsonLine["message"]["charId"]) < 0:
                ssCardAddUser.append(jsonLine["message"]["charId"])

        # stat day >=scard source log
        # cardType should be scard or even higher
        if jsonLine["message"]["cardQuality"] >= S_CARD_LABEL:
            if (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_CREATE_ROLE")
                and jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_CREATE_ROLE_A")):
                if(cardSourceNumDic.has_key("CARD_CREATE_ROLE")):
                    cardSourceNumDic["CARD_CREATE_ROLE"] += 1
                else:
                    cardSourceNumDic["CARD_CREATE_ROLE"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_GIFT_ADD")):
                if(cardSourceNumDic.has_key("CARD_GIFT_ADD")):
                    cardSourceNumDic["CARD_GIFT_ADD"] += 1
                else:
                    cardSourceNumDic["CARD_GIFT_ADD"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_BOSSDROP_ADD")):
                if(cardSourceNumDic.has_key("CARD_BOSSDROP_ADD")):
                    cardSourceNumDic["CARD_BOSSDROP_ADD"] += 1
                else:
                    cardSourceNumDic["CARD_BOSSDROP_ADD"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_WEIXIN")):
                if(cardSourceNumDic.has_key("CARD_WEIXIN")):
                    cardSourceNumDic["CARD_WEIXIN"] += 1
                else:
                    cardSourceNumDic["CARD_WEIXIN"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_COMB_ADD")):
                if(cardSourceNumDic.has_key("CARD_COMB_ADD")):
                    cardSourceNumDic["CARD_COMB_ADD"] += 1
                else:
                    cardSourceNumDic["CARD_COMB_ADD"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_GACHA_ADD")):
                index = gacha_types.index(jsonLine["message"]["gachaCardType"])
                type_name = gacha_types_names[index]
                if(cardSourceNumDic.has_key(type_name)):
                    cardSourceNumDic[type_name] += 1
                else:
                    cardSourceNumDic[type_name] = 1

        # stat day gacha add log






        # stat day card operate num



            #def


# transform object to dictionary
def object2dict(obj):
    d = {}
    #d["__class__"] = obj.__class__.__name__
    #d["__module__"] = obj.__module__
    d.update(obj.__dict__)
    return d


def loadGachaExcel():
    # load gacha type info
    data = xlrd.open_workbook(gacha_excel_path)
    table = data.sheets()[3]

    global gacha_types
    global gacha_types_names

    # load gacha types
    types = table.col_values(0)
    for i in range(5, len(types), 1):
        gacha_types.append(int(types[i]))

    # load gacha types names
    gacha_types_names = table.col_values(1)
    for i in range(0, 5, 1):
        gacha_types_names.pop(0)



loadGachaExcel()

for line in open(card_log_path):
    jsonLine = cardlogtojson(line, )
    # stat day_sscard_add info
    dayCardStat(jsonLine)
    #


# output sscard_add_stat into log file
sscard_add_stat_object = SSCardAddStatBean(gameCode, serverId, regionId, ssCardAddNum, len(ssCardAddUser), timestamp)
sscard_add_stat_log = object2dict(sscard_add_stat_object)
output = open(sscard_add_stat_path, 'a')
try:
    output.write(("{'message':" + str(sscard_add_stat_log) + "}").replace("'", "\"") + "\n")
finally:
    output.close()


