ps -efa|grep keepalive.sh |grep -v grep | awk ' { print $2 }'| xargs kill -9
ps -efa|grep python |grep -v grep | awk ' { print $2 }' |xargs kill -9
/root/scripts/stopredis.sh
