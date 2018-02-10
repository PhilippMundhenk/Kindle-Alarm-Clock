class Alarm():
	weekdays=[]
	hour=-1
	minute=-1
	active=False
	
	def __init__(self, days, hour, minute):
		self.weekdays=days
		self.hour=hour
		self.minute=minute
		self.active=True

	def setActive(self, active):
		self.active=active

	def getActive(self):
		return self.active