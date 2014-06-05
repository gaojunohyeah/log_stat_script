#!/bin/sh
GAMECODE="pokersg"
REGIONID="1"
SERVERID="1001"
echo  "30 0 * * * /usr/bin/python /data/log_stat/script/day_card_stat.py ${GAMECODE} ${REGIONID} ${SERVERID} > /dev/null 2>&1"  >> /var/spool/cron/root
echo  "45 0 * * * /usr/bin/python /data/log_stat/script/day_dungeon_stat.py ${GAMECODE} ${REGIONID} ${SERVERID} > /dev/null 2>&1"  >> /var/spool/cron/root
echo  "0 1 * * * /usr/bin/python /data/log_stat/script/day_friend_stat.py ${GAMECODE} ${REGIONID} ${SERVERID} > /dev/null 2>&1"  >> /var/spool/cron/root
echo  "15 1 * * * /usr/bin/python /data/log_stat/script/day_gift_stat.py ${GAMECODE} ${REGIONID} ${SERVERID} > /dev/null 2>&1"  >> /var/spool/cron/root
echo  "30 1 * * * /usr/bin/python /data/log_stat/script/day_jade_stat.py ${GAMECODE} ${REGIONID} ${SERVERID} > /dev/null 2>&1"  >> /var/spool/cron/root
echo  "45 1 * * * /usr/bin/python /data/log_stat/script/day_vip_stat.py ${GAMECODE} ${REGIONID} ${SERVERID} > /dev/null 2>&1"  >> /var/spool/cron/root
echo  "0 2 * * * /usr/bin/python /data/log_stat/script/day_recharge_stat.py > /dev/null 2>&1"  >> /var/spool/cron/root
echo  "15 2 * * * /usr/bin/python /data/log_stat/script/day_user_operation_stat.py ${GAMECODE} ${REGIONID} ${SERVERID} > /dev/null 2>&1"  >> /var/spool/cron/root
echo  "30 2 * * * /usr/bin/python /data/log_stat/script/day_player_stat.py ${GAMECODE} ${REGIONID} ${SERVERID} > /dev/null 2>&1"  >> /var/spool/cron/root
echo  "45 2 * * * sh /data/log_stat/script/push_log_files.sh ${SERVERID} > /dev/null 2>&1"  >> /var/spool/cron/root
