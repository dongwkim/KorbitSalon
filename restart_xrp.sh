#!/bin/bash
runcnt=`ps -ef|grep korbit_traing_xrtp  | wc -l`
stamp=`date +%Y%m%d`
if [[ $runcnt == 1 ]]
then
  echo "Trading is running"
else
  echo "Restart Trader"
  ps -ef |grep korbit_trading_xrp |grep -v 'grep' | awk '{print $2}' | xargs kill -9
  nohup /bin/python3 -u /korbit/KorbitSalon/korbit_trading_xrp.py >> /korbit/KorbitSalon/tracelog/trading_xrp.$stamp.log &
fi
