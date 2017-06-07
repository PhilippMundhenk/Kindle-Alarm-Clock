{
   sleep 60
   #killall python httpserver.py
   #killall python alarmServer.py
   mntroot rw
   mkfifo /tmp/test.fifo
   cd /mnt/us/alarm
   python httpserver.py >> /mnt/us/alarm/log_http.log 2>&1 &
   python alarmServer.py >> /mnt/us/alarm/log_alarm.log 2>&1 &
   sleep 10
   /mnt/us/extensions/WebLaunch/bin/start.sh
} &
return 0
