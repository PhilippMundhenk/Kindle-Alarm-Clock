import os
import time
from settings import volume
import subprocess
from subprocess import call

class AudioControl():
	@staticmethod
	def phaseIn(stepSize):
		global volume
		command = "(/mnt/us/mplayer/mplayer -loop 0 -cache 1024 -volume 0 -playlist /mnt/us/alarm/playlist.m3u -input file=/tmp/test.fifo -ao alsa -slave -quiet </dev/null >/mnt/us/alarm/log_mplayer.log 2>&1)&"
		os.system(command)
		command = "(sleep 1 && echo \"set_property volume 0\" > /tmp/test.fifo)&"
		os.system(command)
		time.sleep(10);
		maxVol=volume
		for i in range(0,maxVol,stepSize):
			command="(sleep "+str(i)+" && echo \"set_property volume "+str(i)+"\" && echo \"set_property volume "+str(i)+"\" > /tmp/test.fifo)&"
			os.system(command)

	@staticmethod
	def isMplayerRunning():
		ps= subprocess.Popen("ps -ef | grep mplayer | grep -v grep", shell=True, stdout=subprocess.PIPE)
		output = ps.stdout.read()
		ps.stdout.close()
		ps.wait()
		return output