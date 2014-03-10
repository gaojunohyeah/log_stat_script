#!/usr/bin/python
import json
import xlrd
import time
import datetime
import os
# init var of base
gameCode = "pokersg"
serverId = "1001"
regionId = "1"
timestamp = str(long(time.time() * 1000))
yestodayLogName = "." + str(datetime.date.today() - datetime.timedelta(days=1)) + ".log"
# init file path
card_log_path = "E:/work/workspace/sgpoker/logs/stat/card_log.log"

sscard_add_stat_path = "E:/work/workspace/sgpoker/logs/stat/sscard_add_stat.log"
scard_source_stat_path = "E:/work/workspace/sgpoker/logs/stat/scard_source_stat.log"
user_operation_midfile_path = "E:/work/workspace/sgpoker/logs/stat/user_operate_midfile.log"

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
sscardSourceStatMap = {}
userOperationNumDic = {}

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


# function : logtojson
# load log file line to json object
def logtojson(line):
    # print line
    s = json.loads(line)
    return s


# function : dayCardStat
# stat card_log
def dayCardStat(jsonLine):
    global ssCardAddNum

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
                if (cardSourceNumDic.has_key("CARD_CREATE_ROLE")):
                    cardSourceNumDic["CARD_CREATE_ROLE"] += 1
                else:
                    cardSourceNumDic["CARD_CREATE_ROLE"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_GIFT_ADD")):
                if (cardSourceNumDic.has_key("CARD_GIFT_ADD")):
                    cardSourceNumDic["CARD_GIFT_ADD"] += 1
                else:
                    cardSourceNumDic["CARD_GIFT_ADD"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_BOSSDROP_ADD")):
                if (cardSourceNumDic.has_key("CARD_BOSSDROP_ADD")):
                    cardSourceNumDic["CARD_BOSSDROP_ADD"] += 1
                else:
                    cardSourceNumDic["CARD_BOSSDROP_ADD"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_WEIXIN")):
                if (cardSourceNumDic.has_key("CARD_WEIXIN")):
                    cardSourceNumDic["CARD_WEIXIN"] += 1
                else:
                    cardSourceNumDic["CARD_WEIXIN"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_COMB_ADD")):
                if (cardSourceNumDic.has_key("CARD_COMB_ADD")):
                    cardSourceNumDic["CARD_COMB_ADD"] += 1
                else:
                    cardSourceNumDic["CARD_COMB_ADD"] = 1
            elif (jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_GACHA_ADD")):
                index = gacha_types.index(jsonLine["message"]["gachaCardType"])
                type_name = gacha_types_names[index]
                if (cardSourceNumDic.has_key(type_name)):
                    cardSourceNumDic[type_name] += 1
                else:
                    cardSourceNumDic[type_name] = 1

                    # stat day gacha add log


    # stat day card operate num
    if jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_COMB_ADD"):
        if (userOperationNumDic.has_key("CARD_COMB_ADD")):
            userOperationNumDic["CARD_COMB_ADD"] += 1
        else:
            userOperationNumDic["CARD_COMB_ADD"] = 1
    elif jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_GACHA_ADD"):
        if (userOperationNumDic.has_key("CARD_GACHA_ADD")):
            userOperationNumDic["CARD_GACHA_ADD"] += 1
        else:
            userOperationNumDic["CARD_GACHA_ADD"] = 1
    elif jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_HECHENG_CONSUME_DEL"):
        if (userOperationNumDic.has_key("CARD_HECHENG_CONSUME_DEL")):
            userOperationNumDic["CARD_HECHENG_CONSUME_DEL"] += 1
        else:
            userOperationNumDic["CARD_HECHENG_CONSUME_DEL"] = 1
    elif jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_CHANGE"):
        if (userOperationNumDic.has_key("CARD_CHANGE")):
            userOperationNumDic["CARD_CHANGE"] += 1
        else:
            userOperationNumDic["CARD_CHANGE"] = 1
    elif jsonLine["message"]["reason"] == cardLogReasonDic_Get.get("CARD_A_CHANGE"):
        if (userOperationNumDic.has_key("CARD_A_CHANGE")):
            userOperationNumDic["CARD_A_CHANGE"] += 1
        else:
            userOperationNumDic["CARD_A_CHANGE"] = 1


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

    # load gacha types
    types = table.col_values(0)
    for i in range(5, len(types), 1):
        gacha_types.append(int(types[i]))

    # load gacha types names
    gacha_types_names = table.col_values(1)
    for i in range(0, 5, 1):
        gacha_types_names.pop(0)


# load gacha excel config info
loadGachaExcel()

if os.path.exists(card_log_path + yestodayLogName):
    card_log_path += yestodayLogName
# do stat
for line in open(card_log_path):
    jsonLine = logtojson(line, )
    # stat card log info
    dayCardStat(jsonLine)
    #


# output sscard_add_stat into log file
sscard_add_stat_object = SSCardAddStatBean(gameCode, serverId, regionId, ssCardAddNum, len(ssCardAddUser), timestamp)
sscard_add_stat_log = object2dict(sscard_add_stat_object)
sscard_add_file = open(sscard_add_stat_path, 'a')
try:
    sscard_add_file.write(("{'message':" + str(sscard_add_stat_log) + "}").replace("'", "\"") + "\n")
finally:
    sscard_add_file.close()

# output scard_source_stat into log file
sscardSourceStatMap["gameCode"] = gameCode
sscardSourceStatMap["serverId"] = serverId
sscardSourceStatMap["regionId"] = regionId
sscardSourceStatMap["timestamp"] = timestamp
for key, value in cardSourceNumDic.items():
    sscardSourceStatMap[key] = value
scard_source_file = open(scard_source_stat_path, 'a')
try:
    scard_source_file.write(("{'message':" + json.dumps(sscardSourceStatMap) + "}").replace("'", "\"") + "\n")
finally:
    scard_source_file.close()

# output card operate num into middle log file
card_operate_file = open(user_operation_midfile_path, 'a')
try:
    for key, value in userOperationNumDic.items():
        card_operate_file.write("{\"" + str(key) + "\":" + str(value) + "}\n")
finally:
    card_operate_file.close()
