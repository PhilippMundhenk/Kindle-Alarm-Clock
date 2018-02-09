from BaseHTTPServer import BaseHTTPRequestHandler
import re
from datetime import datetime
from threading import Thread
from subprocess import call
from urlparse import parse_qs

from alarm import Alarm
from alarmControl import AlarmControl
from audioControl import AudioControl

weekdayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

class RestHTTPRequestHandler(BaseHTTPRequestHandler):
	def getClock(self):
		global weekdayNames
		with open('clock.html', 'r') as file:
			numberAlarms=0
			nowCompare=datetime.now()
			minDiff=8*24*60*60
			alarm=Alarm(0,0,0)
			day=0
			for i in AlarmControl().getAlarms():
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
						#print "tdelta: "+str(tdelta)
						#print "daydiff: "+str(dayDiff)
						diff=tdelta.seconds+dayDiff*24*60*60
						#print "diff: "+str(diff)

						if diff<minDiff:
							minDiff=diff
							alarm=i
							day=x
				else:
					numberAlarms=numberAlarms+1
					s2=str(i.hour)+":"+str(i.minute)+":00"
					s1=str(nowCompare.hour)+":"+str(nowCompare.minute)+":00"
					FMT = '%H:%M:%S'
					tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
					#dayDiff = 1
					if tdelta.days==-1:
						dayDiff=1
					else:
						dayDiff=0
					#print "tdelta: "+str(tdelta)
					#print "daydiff: "+str(dayDiff)
					#diff=tdelta.seconds+dayDiff*24*60*60
					diff=tdelta.seconds
					#print "diff: "+str(diff)

					if diff<minDiff:
						minDiff=diff
						alarm=i
						day=nowCompare.weekday()+dayDiff
						
			if(numberAlarms>0):
				print "closest alarm is: "+weekdayNames[day]+", "+str(alarm.hour)+":"+str(alarm.minute)
				text=""+weekdayNames[day]+", "
				text=text+str(alarm.hour).zfill(2) +":"+str(alarm.minute).zfill(2)			
			if(numberAlarms>1):
				text=text+" +"+str(numberAlarms-1)
				return file.read().replace("$NEXT_ALARM$",text)
			else:
				return file.read().replace("$NEXT_ALARM$", "")
			
	def flushScreen(x):
		call(["/mnt/us/alarm/flushScreen.sh"])
	def startRing(self, i):
		global stream
	def do_GET(self):
		if None != re.search('/ring', self.path):
			self.send_response(200)
			self.end_headers()
			dur=5
			self.wfile.write("ringing for "+str(dur)+" seconds...")
			Thread(target=self.ring, args=[dur]).start()
		elif None != re.search('/stop', self.path):
			self.send_response(200)
			self.end_headers()
			AlarmControl().stopAlarm()
		elif None != re.search('/clock', self.path):
			self.send_response(200)
			self.end_headers()
			self.wfile.write(self.getClock())
			Thread(target=self.flushScreen, args=[]).start()
		elif None != re.search('/delall', self.path):
			#AlarmControl().setAlarms([])
			AlarmControl().deleteAllAlarms()
			self.send_response(200)
			self.end_headers()
			self.wfile.write(self.getClock())
		elif None != re.search('/del', self.path):

			#TODO: remove
			self.send_response(200)
			self.end_headers()
			self.wfile.write(self.getClock())
			#TODO: fix this! Cannot just delete alarms like this. Need to check which one to delete!
			# parameters=parse_qs(self.path[5:])
			# AlarmControl.pop(int(parameters['id'][0]))
			# AlarmControl.saveAlarms()
			# self.send_response(200)
			# self.end_headers()
			# self.wfile.write(self.getClock())
			# Thread(target=self.flushScreen, args=[]).start()
		elif None != re.search('/radio', self.path):
			AudioControl.phaseIn(5)
			self.send_response(200)
			self.end_headers()
			self.wfile.write(self.getClock())
		elif None != re.search('/list', self.path):
			self.send_response(200)
			self.end_headers()
			text=""
			if len(AlarmControl().getAlarms())==0:
				text+="<tr><p class=\"text\">No alarms set</p></tr>"
			for idx, i in enumerate(AlarmControl().getAlarms()):
				text=text+"<tr>"
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
			if 'day' in parameters:
				newAlarm = AlarmControl().createAlarm(parameters['hour'][0], parameters['minute'][0], parameters['day'])
			else:
				newAlarm = AlarmControl().createAlarm(parameters['hour'][0], parameters['minute'][0], [])
			print "alarm for: "+str(newAlarm.hour)+":"+str(newAlarm.minute)

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
		
		Thread(target=AlarmControl().WifiOff, args=[]).start()
		return