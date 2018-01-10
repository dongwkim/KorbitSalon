#
# version : 20180110-v1
#
export redisUser=kiwonyoon

# Define keepalive targets in MONITORS variable
#MONITORS=("TokenManager" "XRPDataInsert")
MONITORS=("TokenManager")

checkProceeStatus()
{
	MODULENAME=python
	# SCRIPTNAME stands for shell script who launch Python Module
	SCRIPTNAME=/root/scripts/start$1.sh

	TMPID=`ps -efa | grep $MODULENAME | grep $1 | grep -v grep|awk ' { print $2 }'`

	if [ $TMPID ] ; then
		echo `date '+%F %H:%M:%S'` " PROCESS:: "$1 " : " $TMPID " exist"
	else
        echo `date '+%F %H:%M:%S'` " PROCESS:: "$1 " not exist"
		$SCRIPTNAME
	fi	
	return $TMPID
}

while true
do
	for (( i = 0 ; i < ${#MONITORS[@]} ; i++ )) ; do
		checkProceeStatus ${MONITORS[$i]}
	done
sleep 30
done
