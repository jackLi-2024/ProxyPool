ps -ef|grep lijiacai_alive | awk '{print $2}' | xargs kill -9 >> ./log/alive.log
nohup python run.py >> ./log/alive.log &
rm -rf nohup.out
