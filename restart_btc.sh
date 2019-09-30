#!/bin/bash
while true
do
runcnt=`ps -ef|grep btc_collector  |grep -v 'grep'|grep -v 'vi'|grep -v 'tail'| wc -l`
stamp=`date +%Y%m%d`
timestamp=`date +%Y%m%d-%H%M`
if [[ $runcnt == 1 ]]
then
  echo $timestamp " :Ticker Collection is running"
else
  echo $timestamp " :Restart Ticker Collection"
  ps -ef |grep btc_ticker |grep -v 'grep' |  awk '{print $2}' | xargs kill -9
  nohup /bin/python3 -u /korbit/KorbitSalon/btc_collector.py >> /korbit/KorbitSalon/tracelog/btc_collector_$stamp.log &
fi
sleep 10
done
