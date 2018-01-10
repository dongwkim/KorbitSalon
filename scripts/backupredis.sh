REDISBACKUPDIR=/backup/redis
MYDATE=`date '+%F'`
MYTIMESTAMP=`date '+%F_%H-%M-%S'`
mkdir -p $REDISBACKUPDIR/$MYDATE
wait
cp /root/redis/appendonly.aof $REDISBACKUPDIR/$MYDATE/appendonly.aof.$MYTIMESTAMP
