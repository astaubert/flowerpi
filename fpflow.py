# A. Staubert, 11-2015
#
# This library implements the functions to interface with the waterflow sensor via GPIO
#

import RPi.GPIO as GPIO
import time

# Import this module for generic logging used in flowerpi project
import fplog

# Set to the GPIO required to monitor the waterflow sensor (BCM notation!)
GPIO_WATERFLOW_SENSOR = 22

# Set to the GPIO required to activate the blue LED (BCM notation!)
GPIO_BLUE_LED = 7

# Function to check for start of waterflow, second = lenght of timeout, return value = "True" if timeout kicked in
#
def wfstart(second, logtype="prod"):

	fplog.l("=> in fpflow.py/wfstart",logtype)

	start = 0
	signal = False
	timestart = time.clock()
	timeout = False

	# Wait for water to flow, unless timeout "seconds" kicks in

	while start<10 and not(timeout):
		start = wfcount(0.1,"yes")
		if time.clock()-timestart > second:
			timeout = True

	fplog.l("<= out wfstart, return value: timeout = " + str(timeout),logtype)
	return timeout

# Function to count the waterflow; second = time of counting, return value = counts
#
def wfcount(second, logtype="prod"):
	fplog.l("=> in fpflow.py/wfcount",logtype)

	count = 0
	signal = False

	# st Start Time

	st = time.clock()
	et = st

	# 2015-12-13 change difference below from "second" to "2" (which means 2 seconds)
	
	while (et-st)<2:
		input = GPIO.input(GPIO_WATERFLOW_SENSOR)
		if input and not(signal):
			count += 1
			signal = True

		if not(input) and signal:
			count += 1
			signal = True

		et = time.clock()

	fplog.l("<= out wfcount, return value: count = " + str(count),logtype)
	return count


# ...run automated tests if library is started as a script

if __name__ == "__main__":
	fplog.l("+++ In: fpflow.py Test +++ ","test")

	# BCM (GPIO Nummern) verwenden um mit fprfid compatibel zu sein!
	GPIO.setmode(GPIO.BCM)

	# GPIO_WATERFLOW_SENSOR = input => Sammeln der Impulse vom Waterflow-Sensor
	GPIO.setup(GPIO_WATERFLOW_SENSOR, GPIO.IN)

	# GPIO_BLUE_LED = output => Ansteuerung der blauen LED = Warten auf Waterflow-Sensor
	GPIO.setup(GPIO_BLUE_LED, GPIO.OUT)

	# Blaue LED einschalten
	GPIO.output(GPIO_BLUE_LED, GPIO.HIGH)	

	fplog.l("Waiting for water to flow, timeout 4 seconds","test")
	nostart = wfstart(4, "no")	
	
	if nostart:
		fplog.l("Timout kicked in, no water is flowing","test")
		GPIO.output(GPIO_BLUE_LED, GPIO.LOW)

	else:
		count = 11		# Initialize counter for loop condition
		totalcount = 0

		while count > 10:
			count = wfcount(0.2,"test")
			totalcount += count
			if GPIO.input(GPIO_BLUE_LED) == 1:
				GPIO.output(GPIO_BLUE_LED, GPIO.LOW)
			else:
				GPIO.output(GPIO_BLUE_LED, GPIO.HIGH)

		fplog.l("=> Final pulses from wfcount:" + str(totalcount),"test")

	fplog.l("+++ Goodby from: fppost.py Test +++","test")

	GPIO.cleanup()