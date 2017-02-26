{
   sleep 60
   cd /mnt/us/alarm
   python httpserver.py & > /dev/null 2>&1
   python testServer.py & > /dev/null 2>&1
   sleep 10
   /mnt/us/extensions/WebLaunch/bin/start.sh
} &
return 0
