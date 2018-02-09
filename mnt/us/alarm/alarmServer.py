from BaseHTTPServer import HTTPServer
import cgi
import json
import os.path
import commands
import time
import pickle

from threading import Thread

from alarmControl import AlarmControl
from alarm import Alarm
from audioControl import AudioControl
from restHTTPRequestHandler import RestHTTPRequestHandler

def invertDisplayIn(i):
	time.sleep(i)
	call(["/mnt/us/alarm/flushScreen.sh"])
	Thread(target=invertDisplayIn, args=[i]).start()

filePathAlarmsBak = '/mnt/us/alarm/alarms.bak'
try:
	if os.path.exists(filePathAlarmsBak):
		if os.stat(filePathAlarmsBak).st_size == 0:
			os.remove(filePathAlarmsBak)
		file2 = open(r'/mnt/us/alarm/alarms.bak', 'rb')
		alarms = pickle.load(file2)
		file2.close()

		print "loading alarms from file..."
		for a in alarms:
			newAlarm = AlarmControl().createAlarm(a.hour, a.minute, a.weekdays)
			print "alarm for: "+str(newAlarm.hour)+":"+str(newAlarm.minute)
except IOError:
	print "no file found, no alarms to load..."
Thread(target=invertDisplayIn, args=[3600]).start()
		
httpd = HTTPServer(('127.0.0.1', 8000), RestHTTPRequestHandler)

while True:
	httpd.handle_request()
