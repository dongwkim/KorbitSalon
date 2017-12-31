ps -ef |grep TokenManager |grep -v 'grep' | awk '{print $2}' | xargs kill -9
nohup python -u ./token/TokenManager.py >> ./logging/TokenManager.log &
