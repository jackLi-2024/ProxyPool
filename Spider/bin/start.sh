ps -ef|grep lijiacai_spider | awk '{print $2}' | xargs kill -9
nohup python tasks.py >> ./log/proxy.log &
rm -rf nohup.out
