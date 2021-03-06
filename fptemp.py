# Staubert 15.01.17
# Based on: https://www.modmypi.com/blog/ds18b20-one-wire-digital-temperature-sensor-and-the-raspberry-pi

import os
import time
import datetime

# Import other libraries required to store the temperature value on Heroku:

import requests
import json

# URL of web application
USEURL = 'https://gentle-taiga-6367.herokuapp.com'

# We then need to load our drivers. Comment Staubert - not required since already loaded on boot time via /etc/modules

# os.system('modprobe w1-gpio')
# os.system('modprobe w1-therm')

# The next step is to define our sensors output file (the w1_slave file) 

temp_sensor = '/sys/bus/w1/devices/10-0008032a0b1e/w1_slave'

# We then need to define a variable for our raw temperature value (temp_raw)
#
def temp_raw():

    f = open(temp_sensor, 'r')
    lines = f.readlines()
    f.close()

    return lines

# Now we read and parse the temperature
#
def read_temp():

    lines = temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = temp_raw()

    # Once the YES signal has been received, we proceed to our second line of output
    temp_output = lines[1].find('t=')

    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string) / 1000.0
        
	return temp_c

# Function to create standardaized log entries
#
def templog(value):

	#added to normalize unicode values to ascii values, not to get problems with printout on console
	#based on: http://stackoverflow.com/questions/1207457/convert-a-unicode-string-to-a-string-in-python-containing-extra-symbols
	value.encode('ascii','ignore')

	stamp = str(datetime.datetime.now()).split('.')[0]
	logstring = "templog " + stamp + ": " + str(value)

	print logstring

	myfile = open("fptemp.log", "a")
	myfile.write(logstring)
	myfile.write("\n")
	myfile.close()


# Read Serial Number of Raspberry Pi - identifies watering can
#
def getserial():

	# Extract serial from cpuinfo file
	cpuserial = "0000000000000000"

	try:
		f = open('/proc/cpuinfo','r')
		for line in f:
			if line[0:6]=='Serial':
				cpuserial = line[10:26]
		f.close()
	except:
		cpuserial = "ERROR000000000"

	return cpuserial

# Function to query if web-site is active
#
def poquerysite():

	templog("=> in poquerysite") 

	error = True
	while error:
		try:
			templog('Try to query site: ' + str(USEURL))
			r = requests.get(USEURL)
			error = False
		except:
			templog('Error: Site not accessible')
			error = True

	templog('Got response from URL: ' + str(r)) 

	sitestatus = "False"
	if r.status_code == 200:
		sitestatus = "True"

	templog("<= out poquerysite, return value: sitestatus = " + str(sitestatus))

	return sitestatus
		
# Function to upload temperature reading to web-site
#
def pushtemp(tempc,time,heater,location):
	
	templog("==> in pushtemp")
	
	payload = {'pisn': PISERIAL, 'location': location, 'tempc' : tempc, 'tempf': time, 'statusheater': heater}
	
	r = requests.post(USEURL + '/temperatures.json', json=payload)

	if r.status_code == 201:
		templog("... success in creating new temperature record")
		flower_hash = json.loads(r.text)
		
	else:
		templog("Sorry, was not able to create a new temperature record")
		templog('Response code is: ' + str(r.status_code))
		templog('Response text is: ' + str(r.text))

	templog("==> out pushtemp")
	
	return
	
# Function get location of can from internet via 'temploc'
#
def gettemploc(pisn):
	
	templog("==> in gettemploc")
	
	r = requests.get(USEURL + '/locquery/' + str(pisn))
	templog(r.text)
			
	location_hash = json.loads(r.text)

	location = str(location_hash["location"])
	location.encode('ascii','ignore')		
	templog('The read location is: '+ location)

	timedeltas = str(location_hash["timedelta"])
	timedeltas.encode('ascii','ignore')
	timedelta = int(timedeltas)	
			
	templog('The timedelta is: '+ str(timedelta))

	templog("==> out gettemploc")	
	
	return location,timedelta


# ################
# MAIN APPLICATION

# Initialize

templog("PHASE0: Main Program Start")

deltatime = 30  # Initial time until a next reading will happen
statusheater = 'off'  # Initial status of external heater
location = '-dummy-'  # Initial status of where the can is located

templog("Try to get PI serial number")  # Get serial number of PI who takes the temperature reading
PISERIAL = getserial()

templog("Try to connect to web-site")  # See if internet connection works
poquerysite()

# Loop

templog("PHASE1: Main Program Loop")

while True:
		tempc = read_temp()	# Read temperature
		
		templog("Temperature [Celsius]: " + str(tempc))
		templog("Status of heater: " + statusheater)
		
		location,deltatime = gettemploc(PISERIAL)  # Read location and time to next reading from Internet (flowepiheroku)
		
		templog("Location of can: " + location)
		templog("Time to next reading [min]: " + str(deltatime))
		
		pushtemp(tempc,deltatime,statusheater,location) # Write temperature to Internet (flowepiheroku)
		
		time.sleep(deltatime*60)  # Wait until next measurement