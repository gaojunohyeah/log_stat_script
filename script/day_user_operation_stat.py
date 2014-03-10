#!/usr/bin/python
import json
import time
# init var of base
gameCode = "pokersg"
serverId = "1001"
regionId = "1"
timestamp = str(long(time.time() * 1000))
# init file path
user_operation_stat_path = "E:/work/workspace/sgpoker/logs/stat/user_operation_stat.log"
user_operation_midfile_path = "E:/work/workspace/sgpoker/logs/stat/user_operate_midfile.log"
# global attribute
userOperationStatMap = {}


# output scard_source_stat into log file
userOperationStatMap["gameCode"] = gameCode
userOperationStatMap["serverId"] = serverId
userOperationStatMap["regionId"] = regionId
userOperationStatMap["timestamp"] = timestamp
user_operation_midfile_file = open(user_operation_midfile_path, 'r+')
for line in user_operation_midfile_file:
    jsonline = json.loads(line)
    for key in jsonline.keys():
        userOperationStatMap[key] = jsonline[key]

# output card operate num into middle log file
user_operation_file = open(user_operation_stat_path, 'a')
try:
    user_operation_file.write(("{'message':" + json.dumps(userOperationStatMap) + "}").replace("'", "\"") + "\n")
    # truncate the user_operation_midfile_file
    user_operation_midfile_file.truncate(0)
finally:
    user_operation_file.close()
