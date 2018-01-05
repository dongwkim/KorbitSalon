ps -ef |grep korbit_trading_xrp |grep -v 'grep' | awk '{print $2}' | xargs kill -9
nohup python3 -u korbit_trading_xrp.py >> ./tracelog/trading_xrp.log &
