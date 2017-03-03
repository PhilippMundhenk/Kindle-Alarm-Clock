{
   sleep 60
   #killall python httpserver.py
   #killall python alarmServer.py
   cd /mnt/us/alarm
   python httpserver.py & > /dev/null 2>&1
   python alarmServer.py & > /dev/null 2>&1
   sleep 10
   /mnt/us/extensions/WebLaunch/bin/start.sh
} &
return 0
