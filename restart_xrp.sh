#!/bin/bash
while true
do
runcnt=`ps -ef|grep korbit_trading_xrp  | wc -l`
stamp=`date +%Y%m%d`
timestamp=`date +%Y%m%d-%H%M`
if [[ $runcnt == 2 ]]
then
  echo $timestamp " :Trading is running"
else
  echo $timestamp " :Restart Trader"
  ps -ef |grep korbit_trading_xrp |grep -v 'grep' | awk '{print $2}' | xargs kill -9
  nohup /bin/python3 -u /korbit/KorbitSalon/korbit_trading_xrp.py >> /korbit/KorbitSalon/tracelog/trading_xrp.$stamp.log &
fi
sleep 60
done
