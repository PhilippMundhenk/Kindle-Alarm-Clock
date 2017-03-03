from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from subprocess import call
from threading import Thread
import cgi
import json
import time
import os.path
import re
from urlparse import parse_qs
import datetime
from datetime import datetime, timedelta

alarms = []
weekdayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
mplayerMode="playall" #playlist

class Alarm():
	weekday=-1
	hour=-1
	minute=-1
	nextRing=-1
	
	def __init__(self, day, hour, minute, nextRing):
		self.weekday=day
		self.hour=hour
		self.minute=minute
		self.nextRing=nextRing
	def __cmp__(self, other):
		if self.nextRing < other.nextRing:
			return -1
		elif self.nextRing > other.nextRing:
			return 1
		else:
			return 0

class RestHTTPRequestHandler(BaseHTTPRequestHandler):
	def getClock(self):
		global alarms
		global weekdayNames
		with open('clock.html', 'r') as file:
			if(len(alarms) > 0):
				numberAdditionalAlarms=len(alarms)-1
				text=""
				if(alarms[0].weekday >= 0):
					text=text+weekdayNames[int(alarms[0].weekday)]+", "
				text=text+str(alarms[0].hour).zfill(2) +":"+str(alarms[0].minute).zfill(2)
				if(numberAdditionalAlarms>0):
					text=text+" +"+str(numberAdditionalAlarms)
				return file.read().replace("$NEXT_ALARM$",text)
			else:
				return file.read().replace("$NEXT_ALARM$","")
	def flushScreen(x):
		call(["/mnt/us/alarm/flushScreen.sh"])
	def WifiOff(self):
		time.sleep(5)
		call(["ifdown","wlan0"])
	def stopRingIn(self, i):
		time.sleep(i)
		call(["/mnt/us/mplayer/control.sh", "stop"])
	def ringIn(self, i):
		global alarms
		time.sleep(i-10)
		call(["ifup","wlan0"])
		time.sleep(10)
		call(["/mnt/us/mplayer/control.sh", mplayerMode])
		Thread(target=self.stopRingIn, args=[60]).start()
		old = alarms.pop(0)
		if old.weekday != -1:
			seconds=604800 #7 days
			Thread(target=self.ringIn, args=[seconds]).start()
			nextRing=datetime.now()+timedelta(seconds=seconds)
			alarms.append(Alarm(old.weekday,old.hour,old.minute,nextRing))
			alarms=sorted(alarms)
			print "alarm for: day "+str(old.weekday)+" "+str(old.hour)+":"+str(old.minute)
			for i in alarms:
				print i.nextRing
	def ring(self, i):
		call(["/mnt/us/mplayer/control.sh", mplayerMode])
		time.sleep(i)
		call(["/mnt/us/mplayer/control.sh", "stop"])
	def do_GET(self):
		global alarms
		if None != re.search('/ring', self.path):
			self.send_response(200)
			self.end_headers()
			dur=5
			self.wfile.write("ringing for "+str(dur)+" seconds...")
			Thread(target=self.ring, args=[dur]).start()
		elif None != re.search('/stop', self.path):
			self.send_response(200)
			self.end_headers()
			call(["/mnt/us/mplayer/control.sh", "stop"])
		elif None != re.search('/clock', self.path):
			self.send_response(200)
			self.end_headers()
			self.wfile.write(self.getClock())
			Thread(target=self.flushScreen, args=[]).start()
		elif None != re.search('/del', self.path):
			parameters=parse_qs(self.path[5:])
			alarms.pop(int(parameters['id'][0]))
			self.send_response(200)
			self.end_headers()
			self.wfile.write(self.getClock())
			Thread(target=self.flushScreen, args=[]).start()
		elif None != re.search('/list', self.path):
			self.send_response(200)
			self.end_headers()
			text=""
			if len(alarms)==0:
				text+="<tr><p class=\"text\">No alarms set</p></tr>"
			for idx, i in enumerate(alarms):
				text=text+"<tr>"
				if(i.weekday >= 0):
					text=text+"<th class=\"tg-alarm\"><p class=\"text\">"+weekdayNames[int(i.weekday)]+", </th>"
				text=text+"<th class=\"tg-alarm\"><p class=\"text\">"+str(i.hour).zfill(2) +":"+str(i.minute).zfill(2)
				text=text+"</p></th><th class=\"tg-del\"><a href=\"http://localhost:8000/del?id="+str(idx)+"\"><p class=\"text\">del</p></a></th></tr>"
			text=text+"<tr><br/></tr>"
			with open('list.html', 'r') as file:
				self.wfile.write(file.read().replace("$ALARMS$",text))
			Thread(target=self.flushScreen, args=[]).start()
		elif None != re.search('/set', self.path):
			self.send_response(200)
			self.end_headers()
			parameters=parse_qs(self.path[5:])
			now = datetime.now()
			print "current time: "+str(now.hour)+":"+str(now.minute)
			alarmHour=int(parameters['hour'][0])
			alarmMinute=int(parameters['minute'][0])
			if not 'day' in parameters:
				format="%H:%M"
				alarmString=str(alarmHour)+":"+str(alarmMinute)
				diff=datetime.strptime(alarmString, format)-now
				seconds=diff.seconds
				nextRing=datetime.now()+timedelta(seconds=seconds)
				Thread(target=self.ringIn, args=[seconds]).start()
				alarms.append(Alarm(-1,alarmHour, alarmMinute,nextRing))
				alarms=sorted(alarms)
				print "alarm for: "+str(alarmHour)+":"+str(alarmMinute)
				for i in alarms:
						print i.nextRing
				# print "nextRing: "+str(nextRing)
			else:
				for i in range(len(parameters['day'])):
					format="%H:%M"
					weekdayDiff=int(parameters['day'][i])-int(datetime.today().weekday())
					if(weekdayDiff<0):
						weekdayDiff=weekdayDiff+7
					alarmString=str(alarmHour)+":"+str(alarmMinute)
					diff=datetime.strptime(alarmString, format)-now
					weekdayDiffSeconds=((weekdayDiff-1)*24*60*60)
					if(weekdayDiffSeconds<0):
						weekdayDiffSeconds=0
					seconds=diff.seconds+weekdayDiffSeconds
					nextRing=datetime.now()+timedelta(seconds=seconds)
					Thread(target=self.ringIn, args=[seconds]).start()
					alarms.append(Alarm(parameters['day'][i],alarmHour, alarmMinute, nextRing))
					alarms=sorted(alarms)
					print "alarm for: day "+str(parameters['day'][i])+" "+str(alarmHour)+":"+str(alarmMinute)
					for i in alarms:
						print i.nextRing
					# print "nextRing: "+str(nextRing)
			self.wfile.write(self.getClock())
			Thread(target=self.flushScreen, args=[]).start()
		elif None != re.search('/alarm', self.path):
			self.send_response(200)
			self.end_headers()
			with open('alarm.html', 'r') as file:
				self.wfile.write(file.read())
			Thread(target=self.flushScreen, args=[]).start()
		else:
			self.send_response(404)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
		
		Thread(target=self.WifiOff, args=[]).start()
		return
     
httpd = HTTPServer(('127.0.0.1', 8000), RestHTTPRequestHandler)
while True:
	httpd.handle_request()
