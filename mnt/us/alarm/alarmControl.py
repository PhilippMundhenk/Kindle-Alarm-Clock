from datetime import datetime, timedelta
from threading import Thread, Timer
import time
import os
import pickle
import subprocess
from subprocess import call

from settings import secondsToAutoOff
from alarm import Alarm
from settings import wificontrol
from audioControl import AudioControl
from settings import backupSound

class AlarmControl():
	alarms = []
	activeAlarm = None
	
	class __AlarmControl:
		#def __init__(self):
		def __str__(self):
			return repr(self)

	instance = None
	def __init__(self):
		if not AlarmControl.instance:
			AlarmControl.instance = AlarmControl.__AlarmControl()
    
	def __getattr__(self):
		return getattr(self.instance)

	def getAlarms(self):
		return self.alarms

	def deleteAllAlarms(self):
		for a in self.alarms:
			a.setActive(False)
		del self.alarms[:]
		self.saveAlarms()

	def setAlarms(self, alarmsList):
		del self.alarms[:]
		self.append(alarmsList)
		self.saveAlarms()

	def addAlarm(self, alarm):
		print "addAlarm(): "+str(alarm.weekdays)+", "+str(alarm.hour)+":"+str(alarm.minute)
		self.alarms.append(alarm)
		self.saveAlarms()

	def stopAlarm(self):
		print "stopping alarm..."
		for x in self.alarms:
			print "id: "+str(id(x))
			if id(x)==self.activeAlarm and len(x.weekdays)==0:
				print "deleting..."
				alarms.remove(x)
				saveAlarms()
		call(["killall", "mplayer"])

	def createAlarm(self, hour, minute, weekdays):
		print "createAlarm(): "+str(weekdays)+", "+str(hour)+":"+str(minute)

		alarmHour=int(hour)
		alarmMinute=int(minute)
		
		format="%H:%M"
		alarmString=str(alarmHour)+":"+str(alarmMinute)
		now = datetime.now()
		diff=datetime.strptime(alarmString, format)-now
		seconds=diff.seconds
		nextRing=datetime.now()+timedelta(seconds=seconds)
		if len(weekdays) == 0:
			newAlarm = Alarm([], alarmHour, alarmMinute)
		else:
			newAlarm = Alarm([int(i) for i in weekdays], alarmHour, alarmMinute)
		
		self.alarms.append(newAlarm)
		self.saveAlarms()
		t=Thread(target=AlarmControl().ringIn, args=[seconds, newAlarm])
		t.start()
		return newAlarm

	def WifiOn(self):
		global wificontrol
		if wificontrol:
			#Need to turn off WiFi via Kindle Framework first, so that it auto connects when turning on
			call(["lipc-set-prop", "com.lab126.cmd", "wirelessEnable", "0"])
			time.sleep(30)
			call(["lipc-set-prop", "com.lab126.cmd", "wirelessEnable", "1"])
			call(["ifup", "wlan0"])
			time.sleep(10)

	def WifiOff(self):
		global wificontrol
		if wificontrol:
			time.sleep(5)
			call(["ifdown", "wlan0"])
			#Better do not use propper WiFi off here, will trigger UI elements:
			# call(["lipc-set-prop", "com.lab126.cmd", "wirelessEnable", "0"])

	def saveAlarms(self):
		if os.path.exists('/mnt/us/alarm/alarms.bak'):
			os.remove('/mnt/us/alarm/alarms.bak')
		afile = open(r'/mnt/us/alarm/alarms.bak', 'wb')
		pickle.dump(self.alarms, afile)
		afile.close()
		
	def stopRingIn(self, i):
		time.sleep(i)
		self.stopAlarm()
	
	def ringIn(self, i, alarm):
		global stream
		global secondsToAutoOff
		
		time.sleep(i-20)

		#print "today: "+str(datetime.today().weekday())
		#print "days: "+str(alarm.weekdays)

		if not alarm.getActive():
			print "alarm deactivated, exiting..."
			return

		if len(alarm.weekdays) > 0:
			if not datetime.today().weekday() in alarm.weekdays:
				seconds = 24*60*60;
				t=Thread(target=AlarmControl().ringIn, args=[seconds, alarm])
				t.start()
				
				print "seconds: "+str(seconds)
				print "alarm for: days: "+str(alarm.weekdays)+" "+str(alarm.hour)+":"+str(alarm.minute)+" ("+str(seconds)+"seconds)"
					
				return

		print "preparing alarm..."
		self.activeAlarm=id(alarm)

		self.WifiOn()
		AudioControl.phaseIn(1)
		Thread(target=AlarmControl().stopRingIn, args=[secondsToAutoOff]).start()
		
		print "waiting for check..."
		time.sleep(10)
		#ToDo: move this to thread? What if mplayer/wget/pipe cache hangs and there is no sound output? How to detect?
		if(AudioControl.isMplayerRunning()==""):
			command = "/mnt/us/mplayer/mplayer -loop 0 "+backupSound+" &"
			os.system(command)

		#self.alarms.remove(alarm)
		#self.saveAlarms()
		if len(alarm.weekdays) > 0:
			#check in 24h if ring is required
			seconds = 24*60*60;
			t=Thread(target=AlarmControl().ringIn, args=[seconds, alarm])
			t.start()

			print "seconds: "+str(seconds)			
			print "alarm for: days "+str(alarm.weekdays)+" "+str(alarm.hour)+":"+str(alarm.minute)
		else:
			self.alarms.remove(alarm)