{
   killall python httpserver.py
   killall python testServer.py
   cd /mnt/us/alarm
   sleep 2
   python httpserver.py & > /dev/null 2>&1
   python testServer.py & > /dev/null 2>&1
   sleep 2
   /mnt/us/extensions/WebLaunch/bin/start.sh
} &
return 0
