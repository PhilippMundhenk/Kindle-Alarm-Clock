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
wificontrol=False

def invertDisplayIn(i):
	time.sleep(i)
	call(["/mnt/us/alarm/flushScreen.sh"])
	Thread(target=invertDisplayIn, args=[i]).start()

class Alarm():
	weekdays=[]
	hour=-1
	minute=-1
	
	def __init__(self, days, hour, minute):
		self.weekdays=days
		self.hour=hour
		self.minute=minute
			
class AlarmControl():
	@staticmethod
	def WifiOn():
		global wificontrol
		if wificontrol:
			#Need to turn off WiFi via Kindle Framework first, so that it auto connects when turning on
			call(["lipc-set-prop", "com.lab126.cmd", "wirelessEnable", "0"])
			time.sleep(30)
			call(["lipc-set-prop", "com.lab126.cmd", "wirelessEnable", "1"])
			call(["ifup", "wlan0"])
			time.sleep(10)

	@staticmethod
	def isMplayerRunning():
		ps= subprocess.Popen("ps -ef | grep mplayer | grep -v grep", shell=True, stdout=subprocess.PIPE)
		output = ps.stdout.read()
		ps.stdout.close()
		ps.wait()
		return output

	@staticmethod
	def saveAlarms():
		global alarms
		if os.path.exists('/mnt/us/alarm/alarms.bak'):
			os.remove('/mnt/us/alarm/alarms.bak')
		afile = open(r'/mnt/us/alarm/alarms.bak', 'wb')
		pickle.dump(alarms, afile)
		afile.close()
		
	@staticmethod
	def stopRingIn(i):
		time.sleep(i)
		call(["killall", "mplayer"])
	
	@staticmethod
	def ringIn(i, alarm):
		global alarms
		global volume
		global stream
		global secondsToAutoOff
		
		time.sleep(i-20)

		print "today: "+str(datetime.today().weekday())
		print "days: "+str(alarm.weekdays)

		if len(alarm.weekdays) != 0:
			if not datetime.today().weekday() in alarm.weekdays:
				seconds = 24*60*60;
				Thread(target=AlarmControl.ringIn, args=[seconds, alarm]).start()
				
				print "seconds: "+str(seconds)
				print "alarm for: days: "+str(alarm.weekdays)+" "+str(alarm.hour)+":"+str(alarm.minute)+" ("+str(seconds)+"seconds)"
					
				return

		print "preparing alarm..."

		AlarmControl.WifiOn()
		command = "(/mnt/us/mplayer/mplayer -loop 0 -cache 1024 -volume 0 -playlist /mnt/us/alarm/playlist.m3u -input file=/tmp/test.fifo -ao alsa -slave -quiet </dev/null >/mnt/us/alarm/log_mplayer.log 2>&1)&"
		os.system(command)
		command = "(sleep 1 && echo \"set_property volume 0\" > /tmp/test.fifo)&"
		os.system(command)
		time.sleep(10);
		maxVol=volume
		for i in range(0,maxVol):
			#command="(sleep "+str(10*i)+" && amixer sset 'Speaker' "+str(i)+")&"
			command="(sleep "+str(i)+" && echo \"set_property volume "+str(i)+"\" && echo \"set_property volume "+str(i)+"\" > /tmp/test.fifo)&"
			os.system(command)
		Thread(target=AlarmControl.stopRingIn, args=[secondsToAutoOff]).start()
		
		print "waiting for check..."
		time.sleep(10)
		#ToDo: move this to thread? What if mplayer/wget/pipe cache hangs and there is no sound output? How to detect?
		if(AlarmControl.isMplayerRunning()==""):
			command = "/mnt/us/mplayer/mplayer -loop 0 "+backupSound+" &"
			os.system(command)

		alarms.remove(alarm)
		AlarmControl.saveAlarms()
		if len(alarm.weekdays) != 0:
			seconds = 24*60*60;
			Thread(target=AlarmControl.ringIn, args=[seconds, alarm]).start()

			print "seconds: "+str(seconds)			
			print "alarm for: days "+str(alarm.weekdays)+" "+str(alarm.hour)+":"+str(alarm.minute)
	

class RestHTTPRequestHandler(BaseHTTPRequestHandler):
	def getClock(self):
		global alarms
		global weekdayNames
		with open('clock.html', 'r') as file:
			numberAlarms=0
			nowCompare=datetime.now()
			minDiff=8*24*60*60
			alarm=Alarm(0,0,0)
			day=0
			for i in alarms:
				if len(i.weekdays)>0:
					for x in i.weekdays:
						numberAlarms=numberAlarms+1
						s2=str(i.hour)+":"+str(i.minute)+":00"
						s1=str(nowCompare.hour)+":"+str(nowCompare.minute)+":00"
						FMT = '%H:%M:%S'
						tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
						dayDiff = (7 + (x - nowCompare.weekday())) % 7
						if dayDiff==0 and tdelta.days==-1:
							dayDiff=dayDiff+7
						print "tdelta: "+str(tdelta)
						print "daydiff: "+str(dayDiff)
						diff=tdelta.seconds+dayDiff*24*60*60
						print "diff: "+str(diff)

						if diff<minDiff:
							minDiff=diff
							alarm=i
							day=x
				else:
					s2=str(i.hour)+":"+str(i.minute)+":00"
					s1=str(nowCompare.hour)+":"+str(nowCompare.minute)+":00"
					FMT = '%H:%M:%S'
					tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
					dayDiff = 1
					print "tdelta: "+str(tdelta)
					print "daydiff: "+str(dayDiff)
					diff=tdelta.seconds+dayDiff*24*60*60
					print "diff: "+str(diff)

					if diff<minDiff:
						minDiff=diff
						alarm=i
						day=x
						
			print "closest alarm is: "+weekdayNames[day]+", "+str(alarm.hour)+":"+str(alarm.minute)
	
			if(numberAlarms>0):
				text=""+weekdayNames[day]+", "
				text=text+str(alarm.hour).zfill(2) +":"+str(alarm.minute).zfill(2)			
			if(numberAlarms>1):
				text=text+" +"+str(numberAlarms-1)
				return file.read().replace("$NEXT_ALARM$",text)
			else:
				return file.read().replace("$NEXT_ALARM$", "")
			
	def flushScreen(x):
		call(["/mnt/us/alarm/flushScreen.sh"])
	def WifiOff(self):
		global wificontrol
		if wificontrol:
			time.sleep(5)
			call(["ifdown", "wlan0"])
			#Better do not use propper WiFi off here, will trigger UI elements:
			# call(["lipc-set-prop", "com.lab126.cmd", "wirelessEnable", "0"])
	def startRing(self, i):
		global stream
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
		elif None != re.search('/delall', self.path):
			alarms=[]
			AlarmControl.saveAlarms()
			self.send_response(200)
			self.end_headers()
			with open('alarm.html', 'r') as file:
				self.wfile.write(file.read())
		elif None != re.search('/del', self.path):
			parameters=parse_qs(self.path[5:])
			alarms.pop(int(parameters['id'][0]))
			AlarmControl.saveAlarms()
			self.send_response(200)
			self.end_headers()
			self.wfile.write(self.getClock())
			Thread(target=self.flushScreen, args=[]).start()
		elif None != re.search('/radio', self.path):
			global volume

			command = "(/mnt/us/mplayer/mplayer -loop 0 -cache 1024 -volume 0 -playlist /mnt/us/alarm/playlist.m3u -input file=/tmp/test.fifo -ao alsa -slave -quiet </dev/null >/mnt/us/alarm/log_mplayer.log 2>&1)&"
			os.system(command)
			command = "(sleep 1 && echo \"set_property volume 0\" > /tmp/test.fifo)&"
			os.system(command)
			time.sleep(10);
			maxVol=volume
			for i in range(0,maxVol,5):
				#command="(sleep "+str(10*i)+" && amixer sset 'Speaker' "+str(i)+")&"
				command="(sleep "+str(i)+" && echo \"set_property volume "+str(i)+"\" && echo \"set_property volume "+str(i)+"\" > /tmp/test.fifo)&"
				os.system(command)

			self.send_response(200)
			self.end_headers()
			self.wfile.write(self.getClock())
		elif None != re.search('/list', self.path):
			self.send_response(200)
			self.end_headers()
			text=""
			if len(alarms)==0:
				text+="<tr><p class=\"text\">No alarms set</p></tr>"
			for idx, i in enumerate(alarms):
				text=text+"<tr>"
				#TODO: What if no weekdays?
				if(len(i.weekdays) > 0):
					text=text+"<th class=\"tg-alarm\">"+"<p class=\"text\">"
					cnt=0
					for day in i.weekdays:
						cnt=cnt+1
						text=text+weekdayNames[int(day)]
						if(cnt!=len(i.weekdays)):
							text=text+","
					text=text+":</th>"
				else:
					text=text+"<th class=\"tg-alarm\">"+"<p class=\"text\">"+"</th>"
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
			alarmHour=int(parameters['hour'][0])
			alarmMinute=int(parameters['minute'][0])
			
			format="%H:%M"
			alarmString=str(alarmHour)+":"+str(alarmMinute)
			now = datetime.now()
			diff=datetime.strptime(alarmString, format)-now
			seconds=diff.seconds
			nextRing=datetime.now()+timedelta(seconds=seconds)
			if not 'day' in parameters:
				newAlarm = Alarm([], alarmHour, alarmMinute)
			else:
				newAlarm = Alarm([int(i) for i in parameters['day']], alarmHour, alarmMinute)
			
			Thread(target=AlarmControl.ringIn, args=[seconds, newAlarm]).start()
			
			alarms.append(newAlarm)
			AlarmControl.saveAlarms()
				
			print "alarm for: "+str(alarmHour)+":"+str(alarmMinute)+" (in "+str(seconds)+" seconds)"

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

filePathAlarmsBak = '/mnt/us/alarm/alarms.bak'
if os.path.exists(filePathAlarmsBak):
	if os.stat(filePathAlarmsBak).st_size == 0:
		os.remove(filePathAlarmsBak)
	file2 = open(r'/mnt/us/alarm/alarms.bak', 'rb')
	alarms = pickle.load(file2)
	file2.close()

	for a in alarms:
		alarmHour=int(a.hour)
		alarmMinute=int(a.minute)
		print a.weekdays
		format="%H:%M"
		alarmString=str(alarmHour)+":"+str(alarmMinute)
		now = datetime.now()
		diff=datetime.strptime(alarmString, format)-now
		seconds=diff.seconds
		#nextRing=datetime.now()+timedelta(seconds=seconds)
		if len(a.weekdays) == 0:
			newAlarm = Alarm([], alarmHour, alarmMinute)
		else:
			newAlarm = Alarm([int(i) for i in a.weekdays], alarmHour, alarmMinute)
		Thread(target=AlarmControl.ringIn, args=[seconds, newAlarm]).start()
		
		print "alarm for: "+str(alarmHour)+":"+str(alarmMinute)+" (in "+str(seconds)+" seconds)"
		
Thread(target=invertDisplayIn, args=[3600]).start()
		
httpd = HTTPServer(('127.0.0.1', 8000), RestHTTPRequestHandler)

while True:
	httpd.handle_request()
