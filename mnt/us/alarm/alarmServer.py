from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from subprocess import call
from threading import Thread
import cgi
import json
import time
import os.path
import os
import commands
import re
import subprocess
from urlparse import parse_qs
import datetime
from datetime import datetime, timedelta
import pickle
from threading import Timer

alarms = []
weekdayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
backupSound="/mnt/us/music/smsalert2.mp3"
volume=75
secondsToAutoOff=600
wificontrol=True

def invertDisplayIn(self, i):
	time.sleep(i)
	flushScreen()
	Thread(target=self.invertDisplayIn, args=[i]).start()

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
	def isMplayerRunning(self):
		ps= subprocess.Popen("ps -ef | grep mplayer | grep -v grep", shell=True, stdout=subprocess.PIPE)
		output = ps.stdout.read()
		ps.stdout.close()
		ps.wait()
		return output
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
	def saveAlarms(self):
		if os.path.exists('/mnt/us/alarm/alarms.bak'):
			os.remove('/mnt/us/alarm/alarms.bak')
		afile = open(r'/mnt/us/alarm/alarms.bak', 'wb')
		pickle.dump(alarms, afile)
		afile.close()
	def WifiOn(self):
		if wificontrol:
			#Need to turn off WiFi via Kindle Framework first, so that it auto connects when turning on
			call(["lipc-set-prop", "com.lab126.cmd", "wirelessEnable", "0"])
			time.sleep(30)
			call(["lipc-set-prop", "com.lab126.cmd", "wirelessEnable", "1"])
			call(["ifup", "wlan0"])
			time.sleep(10)
	def WifiOff(self):
		if wificontrol:
			time.sleep(5)
			call(["ifdown", "wlan0"])
			#Better do not use propper WiFi off here, will trigger UI elements:
			# call(["lipc-set-prop", "com.lab126.cmd", "wirelessEnable", "0"])
	def stopRingIn(self, i):
		time.sleep(i)
		call(["killall", "mplayer"])
	def startRing(self, i):
		global stream
		
	def ringIn(self, i):
		global alarms
		global volume
		global stream
		global secondsToAutoOff
		time.sleep(i-10)
		self.WifiOn()
		#ToDo: fade-in effect here:
		#command = "(/mnt/us/mplayer/mplayer -loop 0 -cache 1024 -playlist /mnt/us/alarm/playlist.m3u)&"
		command = "mkfifo /tmp/test.fifo"
		os.system(command)
		command = "(/mnt/us/mplayer/mplayer -loop 0 -cache 1024 -volume 100 -playlist /mnt/us/alarm/playlist.m3u -input file=/tmp/test.fifo -ao alsa -slave -quiet </dev/null >/mnt/us/alarm/log_mplayer.log 2>&1)&"
		os.system(command)
		#command = "(sleep 1 && amixer sset 'Speaker' 0)&"
		command = "(sleep 1 && echo \"set_property volume 0\" > /tmp/test.fifo)&"
		os.system(command)
		#Thread(target=self.startRing, args=[6]).start()
		time.sleep(6)
		#command = "(killall mplayer)&"
		#os.system(command)
		time.sleep(1)
		#command = "(/mnt/us/mplayer/mplayer -cache 1024 \""+stream+"\")&"
		#os.system(command)
		time.sleep(10)
		#ToDo: move this to thread? What if mplayer/wget/pipe cache hangs and there is no sound output? How to detect?
		if(self.isMplayerRunning()==""):
			command = "/mnt/us/mplayer/mplayer -loop 0 "+backupSound+" &"
			os.system(command)
		#maxVol=volume/(100/7)
		maxVol=volume
		for i in range(0,maxVol):
			#command="(sleep "+str(10*i)+" && amixer sset 'Speaker' "+str(i)+")&"
			command="(sleep "+str(i)+" && echo \"set_property volume "+str(i)+"\" > /tmp/test.fifo)&"
			os.system(command)
		Thread(target=self.stopRingIn, args=[secondsToAutoOff]).start()
		old = alarms.pop(0)
		self.saveAlarms()
		if old.weekday != -1:
			seconds=604800 #7 days
			Thread(target=self.ringIn, args=[seconds]).start()
			nextRing=datetime.now()+timedelta(seconds=seconds)
			alarms.append(Alarm(old.weekday,old.hour,old.minute,nextRing))
			alarms=sorted(alarms)
			self.saveAlarms()
			
			print "alarm for: day "+str(old.weekday)+" "+str(old.hour)+":"+str(old.minute)
			for i in alarms:
				print i.nextRing
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
			call(["killall", "mplayer"])
		elif None != re.search('/clock', self.path):
			self.send_response(200)
			self.end_headers()
			self.wfile.write(self.getClock())
			Thread(target=self.flushScreen, args=[]).start()
		elif None != re.search('/del', self.path):
			parameters=parse_qs(self.path[5:])
			alarms.pop(int(parameters['id'][0]))
			self.saveAlarms()
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
				alarms.append(Alarm(-1,alarmHour, alarmMinute, nextRing))
				alarms=sorted(alarms)
				self.saveAlarms()
				
				print "alarm for: "+str(alarmHour)+":"+str(alarmMinute)+" (in "+str(seconds)+" seconds)"
				for i in alarms:
						print i.nextRing
				# print "nextRing: "+str(nextRing)
			else:
				for i in range(len(parameters['day'])):
					format="%H:%M"
					weekdayDiff=int(parameters['day'][i])-int(datetime.today().weekday())
					if(weekdayDiff<=0):
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
					self.saveAlarms()
			
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

if os.path.exists('/mnt/us/alarm/alarms.bak'):
	file2 = open(r'/mnt/us/alarm/alarms.bak', 'rb')
	alarms = pickle.load(file2)
	file2.close()
	
Thread(target=invertDisplayIn, args=[0, 3600]).start()
		
httpd = HTTPServer(('127.0.0.1', 8000), RestHTTPRequestHandler)

while True:
	httpd.handle_request()
