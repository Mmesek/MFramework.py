#!/bin/sh
cd /home/pi/MFramework.py/
source /home/pi/MFramework.py/MFramework/bin/activate
/usr/bin/screen -dm -S "MFramework" /home/pi/MFramework.py/MFramework/bin/python3.8 /home/pi/MFramework/__main__.py