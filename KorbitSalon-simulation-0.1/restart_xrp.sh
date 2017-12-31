ps -ef |grep korbit_trading_xrp |grep -v 'grep' | awk '{print $2}' | xargs kill -9
nohup python -u korbit_trading_xrp.py >> ./logging/trading_xrp.log &
