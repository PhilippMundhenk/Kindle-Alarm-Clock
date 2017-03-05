# Kindle-Alarm-Clock
An alarm clock running on the Kindle Touch.

## Description
I wanted an alarm clock with a certain set of features in a nice design at a reasonable price point. Unfortunately, I couldn't find any such thing. I thus decided to build my own. I got a used Kindle Touch, which is, other than the lack of screen lighting, ideal for this purpose: It has a large display, consumes relatively little energy, due to the e-ink display, runs a Linux-based OS and is easy to hack.

Note: I threw this together in the course of a Saturday, so please forgive me, if not everything is absolutely beautiful. Feel free to report errors or contribute!

For more information see [https://www.mundhenk.org/blog/kindle-alarm-clock](https://www.mundhenk.org/blog/kindle-alarm-clock).

## Features
- multiple timers: Set and manage multiple timers
- weekday timers: Set a different recurring timer for every day of the week
- auto-off: Alarm turns off after 1 minute of ringing
- auto-start: starts together with Kindle
- custom sounds: Uses mplayer to play MP3, Internet Radio, ...
- WiFi auto-off: WiFi is turned off automatically, after usage, reducing electromagnetic pollution (your alarm clock really does not need WiFi).
- auto-refresh/invert of e-ink display to avoid ghosting effects, every 10min.

## Photos
![Clock/Home Screen](https://raw.githubusercontent.com/PhilippMundhenk/Kindle-Alarm-Clock/master/photos/clockScreen.jpg "Clock/Home Screen")
![Alarm Settings](https://raw.githubusercontent.com/PhilippMundhenk/Kindle-Alarm-Clock/master/photos/alarmSettings.jpg "Alarm Settings")
![List of Alarms](https://raw.githubusercontent.com/PhilippMundhenk/Kindle-Alarm-Clock/master/photos/ListOfAlarms.jpg "List of Alarms")

## Requirements
- Kindle Touch: Likely also running on other Kindles with speakers, but not tested.
- Jailbreak for Kindle Touch, see [here](https://www.mobileread.com/forums/showthread.php?t=275877)
- USB Networking, see [here](https://www.mobileread.com/forums/showthread.php?t=186645)
- Kindle Unified Applications Launcher (KUAL), see [here](https://www.mobileread.com/forums/showthread.php?t=203326)
- WebLaunch, see [here](https://github.com/PaulFreund/WebLaunch)
- MPlayer, see [here](https://www.mobileread.com/forums/showthread.php?t=119851)
- Python, see [here](https://www.mobileread.com/forums/showthread.php?t=225030)
- Any WiFi around that you can connect to (no need for internet, unless you want to play internet radio)

## Installation
* Follow the instructions on (link: https://wiki.mobileread.com/wiki/Kindle_Touch_Hacking text: MobileRead Wiki popup:yes) to jailbreak your Kindle, install USB Networking, KUAL, WebLaunch, MPlayer and Python, if you haven't already.
* Copy the files from this repository to the root of your Kindle:
   * The actual app components are located in */mnt/us/alarm*.
   * A startup script is located in */etc/upstart*. This way, the alarm clock will automatically start whenever your Kindle starts. There is a bit of delay
   * The **settings.js** file for WebLaunch is located in */mnt/us/extensions/WebLaunch*. This will overwrite your current settings.js, if you use WebLaunch.
* Start WebLaunch manually via KUAL once, so that the settings.js is read.
* Connect your Kindle to any WiFi network. Unfortunately, the Kindle browser (which is used by WebLaunch) only connects to websites, when it is connected to a WiFi, even if the address it connects to is on localhost. Thus, a connectable WiFi needs to be around. The alarm clock will make sure to turn off WiFi whenever it is not needed.
* Place your MP3s (or AAC, FLAC, OGG, ...) to be played at alarm time on the */mnt/us/music* folder and in **alarmServer.py** adjust the following variables:
```
#if you want internet radio, then set this variable to the URL of your radio station. Possibly might have to use the IP address.
stream="http://yourURLHere" 
#the following sound is played if the internet radio station is not available or not set:
backupSound="/path/to/backup/sound/here.mp3"
#this is the volume to play the sound/radio at:
volume=75
```

## Ressources
- excellent summary of the Kindle Touch for DIY people: https://wiki.mobileread.com/wiki/Kindle_Touch_Hacking
- inspiration: 
   - http://blog.yolo.pro/repurposing-an-old-kindle-touch-as-a-weather-display/
   - https://mpetroff.net/2012/09/kindle-weather-display/

