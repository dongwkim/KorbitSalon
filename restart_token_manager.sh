#!/bin/bash
while true
do
runcnt=`ps -ef|grep TokenManager  | wc -l`
stamp=`date +%Y%m%d`
if [[ $runcnt == 2 ]]
then
  echo "TokenMgr is running"
else
  echo "Restart TokenMgr"
  ps -ef |grep TokenManager |grep -v 'grep' | awk '{print $2}' | xargs kill -9
  nohup python3 -u ./TokenManager.py >> ./tracelog/TokenManager.log &
fi
sleep 60
done
