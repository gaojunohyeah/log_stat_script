#!/bin/sh
serverid=$1
today=$(date -d last-day +%Y-%m-%d)
yesdate=$(date -d -2day +%Y-%m-%d)
#echo ${today}

day_online_log_file="/data/game_server/logs/stat/day_online_log.log."${today}".log"
jade_log_file="/data/game_server/logs/stat/jade_log.log."${today}".log"
player_log_file="/data/game_server/logs/stat/player_log.log."${today}".log"

#echo ${day_online_log_file}
#echo ${jade_log_file}
#echo ${player_log_file}
if [ ! -f "$day_online_log_file" ]; then 
 day_online_log_file="/data/game_server/logs/stat/day_online_log.log"
fi
#echo ${day_online_log_file}

if [ ! -f "$jade_log_file" ]; then
 jade_log_file="/data/game_server/logs/stat/jade_log.log"
fi
#echo ${jade_log_file}

if [ ! -f "$player_log_file" ]; then
 player_log_file="/data/game_server/logs/stat/player_log.log"
fi
#echo ${player_log_file}

push_online_path="/data/log_stat/game_logs/"${serverid}"_day_online_log.log."${today}".log"
push_jade_path="/data/log_stat/game_logs/"${serverid}"_jade_log.log."${today}".log"
push_player_log="/data/log_stat/game_logs/"${serverid}"_player_log.log."${today}".log"
#echo ${push_online_path}
#echo ${push_jade_path}
#echo ${push_player_log}

scp -P 5222 ${day_online_log_file} root@211.151.100.239:${push_online_path}
scp -P 5222 ${jade_log_file} root@211.151.100.239:${push_jade_path}
scp -P 5222 ${player_log_file} root@211.151.100.239:${push_player_log}
