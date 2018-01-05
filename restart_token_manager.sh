ps -ef |grep TokenManager |grep -v 'grep' | awk '{print $2}' | xargs kill -9
nohup python3 -u ./TokenManager.py >> ./tracelog/TokenManager.log &
