#!/bin/bash

echo Designed to be run sudo
if [ -z "$1" ]; then
	echo Using venv athomeled3
	source /home/pi/Virtualenvs/athomeled3/bin/activate
else
	echo Using venv $1
	source /home/pi/Virtualenvs/$1/bin/activate
fi
python at_home_led.py
