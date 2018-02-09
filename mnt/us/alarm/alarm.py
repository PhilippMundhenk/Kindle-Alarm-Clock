class Alarm():
	weekdays=[]
	hour=-1
	minute=-1
	
	def __init__(self, days, hour, minute):
		self.weekdays=days
		self.hour=hour
		self.minute=minute