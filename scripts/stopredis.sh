/etc/init.d/redis_6379 stop
ps -efa|grep redis-server|grep -v grep
lsof -i -P -n |grep 16379|grep -v grep
