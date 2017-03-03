{
   killall python httpserver.py
   killall python alarmServer.py
   cd /mnt/us/alarm
   sleep 2
   python httpserver.py & > /dev/null 2>&1
   python alarmServer.py & > /dev/null 2>&1
   sleep 2
   /mnt/us/extensions/WebLaunch/bin/start.sh
} &
return 0
