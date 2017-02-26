# Kindle-Alarm-Clock
An alarm clock running on the Kindle Touch.

## Description
I wanted an alarm clock with a certain set of features in a nice design at a reasonable price point. Unfortunately, I couldn't find any such thing. I thus decided to build my own. I got a used Kindle Touch, which is, other than the lack of screen lighting, ideal for this purpose: It has a large display, consumes relatively little energy, due to the e-ink display, runs a Linux-based OS and is easy to hack.

Note: I threw this together in the course of a Saturday, so please forgive me, if not everything is absolutely beautiful. Feel free to report errors or contribute!

## Features
- multiple timers: Set and manage multiple timers
- weekday timers: Set a different recurring timer for every day of the week
- auto-off: Alarm turns off after 1 minute of ringing
- auto-start: starts together with Kindle
- custom sounds: Uses mplayer to play MP3, Internet Radio, ...
- WiFi auto-off: WiFi is turned off automatically, after usage, reducing electromagnetic pollution (your alarm clock really does not need WiFi).
- auto-refresh of e-ink display to avoid ghosting effects, every 10min.

## Photos
![Clock/Home Screen](https://raw.githubusercontent.com/PhilippMundhenk/Kindle-Alarm-Clock/master/photos/clockScreen.jpg "Clock/Home Screen")
![Alarm Settings](https://raw.githubusercontent.com/PhilippMundhenk/Kindle-Alarm-Clock/master/photos/alarmSettings.jpg "Alarm Settings")
![List of Alarms](https://raw.githubusercontent.com/PhilippMundhenk/Kindle-Alarm-Clock/master/photos/ListOfAlarms.jpg "List of Alarms")

## Requirements
- Kindle Touch: Likely also running on other Kindles, but not tested.
- Jailbreak for Kindle Touch, see [here](https://www.mobileread.com/forums/showthread.php?t=275877)
- USB Networking, see [here](https://www.mobileread.com/forums/showthread.php?t=186645)
- Kindle Unified Applications Launcher (KUAL), see [here](https://www.mobileread.com/forums/showthread.php?t=203326)
- WebLaunch, see [here](https://github.com/PaulFreund/WebLaunch)
- MPlayer, see [here](https://www.mobileread.com/forums/showthread.php?t=119851)
- Python, see [here](https://www.mobileread.com/forums/showthread.php?t=225030)
- Any WiFi around that you can connect to (no need for internet, unless you want to play internet radio)

## Installation
- Follow the instructions on https://wiki.mobileread.com/wiki/Kindle_Touch_Hacking to jailbreak your Kindle, install USB Networking, KUAL, WebLaunch, MPlayer and Python, if you haven't already.
- Copy the files from this repository to the root of your Kindle:
   - The actual app components are located in /mnt/us/alarm.
   - A startup script is located in /etc/upstart. This way, the alarm clock will automatically start whenever your Kindle starts. There is a bit of delay
   - The settings.js file for WebLaunch is located in /mnt/us/extensions/WebLaunch. This will overwrite your current settings.js, if you use WebLaunch.
- Start WebLaunch manually via KUAL once, so that the settings.js is read.
- Connect your Kindle to any WiFi network. Unfortunately, the Kindle browser (which is used by WebLaunch) only connects to websites, when it is connected to a WiFi, even if the address it connects to is on localhost. Thus, a connectable WiFi needs to be around. The alarm clock will make sure to turn off WiFi whenever it is not needed.
- Place your MP3s (or AAC, FLAC, OGG, ...) to be played at alarm time on the /mnt/us/music folder. If you want to use a web address, place it in /mnt/us/mplayer/playlist and in testServer.py set mplayerMode="playlist".

## Usage
- Press beel icon to get to settings screen
- Set your alarm time and repetitions, press set
- Kindle will play your sound file at alarm time
- Press screen to turn off

## ToDo
This project is far from complete, there are a whole lot of things to be done, e.g.
- Integrate the two webservers into one. There is absolutely no need to use, other than my laziness
- Adjust WebLaunch to get rid of the first manual start.
- Persistence of alarms: Currently alarms do not get persisted. After a restart, all alarms are gone and need to be set again.
- Clean up code

## Ressources
- excellent summary of the Kindle Touch for DIY people: https://wiki.mobileread.com/wiki/Kindle_Touch_Hacking
- inspiration: 
   - http://blog.yolo.pro/repurposing-an-old-kindle-touch-as-a-weather-display/
   - https://mpetroff.net/2012/09/kindle-weather-display/

