# A. Staubert, 11-2015
#
# This Python program implements the following functionality:
#
#  - Read an RF ID-tag mounted to a flower (see also: fprfid.py)
#  - Register RF ID-tag at the Ruby on Rails WEB-application "Flowerpiheroku" (if not existing)
#  - Read to amount of water the is applied to the flower, which is measured by a waterflow sensor (see also: fpflow.py)
#  - Store the amount of water applied for the flower in the WEB-application
#

# Import project specific libraries:

import fplog
import fprfid
import fpflow

# Import other libraries:

import RPi.GPIO as GPIO
import time
import requests
import json

# Import this module to gain access to the RFID driver:

import rfid

# Various helper functions:

def abortonerror():

	blinkredled()
	GPIO.output(GPIO_RED_LED, GPIO.HIGH)
	GPIO.output(GPIO_GREEN_LED, GPIO.LOW)
	GPIO.output(GPIO_BLUE_LED, GPIO.LOW)
	GPIO.output(GPIO_YELLOW_LED, GPIO.LOW)

	fplog.l("ABORT ON PREVIOUS ERROR!")
	exit()

def blinkredled():

	for x in range(0,4):
		GPIO.output(GPIO_RED_LED, GPIO.HIGH)
		time.sleep(0.2)
		GPIO.output(GPIO_RED_LED, GPIO.LOW)
		time.sleep(0.2)

def blinkgreenled():

	for x in range(0,4):
		GPIO.output(GPIO_GREEN_LED, GPIO.HIGH)
		time.sleep(0.2)
		GPIO.output(GPIO_GREEN_LED, GPIO.LOW)
		time.sleep(0.2)

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
def poquerysite(logtype="prod"):
	
	fplog.l("=> in poquerysite",logtype) 

	error = True
	while error:
		try:
			fplog.l('Try to query site: ' + str(USEURL),logtype)
			GPIO.output(GPIO_GREEN_LED, GPIO.HIGH)
			r = requests.get(USEURL)
			error = False
		except:
			fplog.l('Error: Site not accessible')
			blinkredled()
			error = True

	fplog.l('Got response from URL: ' + str(r),logtype) 

	tagstatus = "False"
	if r.status_code == 200:
		tagstatus = "True"

	fplog.l("<= out fppost, return value: tagstatus = " + str(tagstatus),logtype)

	return tagstatus

# Function to query if a tag exists
#
def poquerytag(tagsn, logtype="prod"):

	fplog.l("=> in poquerytag",logtype)

	error = True
	while error:
		try:
			GPIO.output(GPIO_GREEN_LED, GPIO.HIGH)
			fplog.l('Query tag: ' + USEURL + '/flowerquery/' + str(tagsn),logtype) 
			r = requests.get(USEURL + '/flowerquery/' + str(tagsn))
			error = False
		except:
			fplog.l('Error: Site not accessible')
			blinkredled()
			error = True

	fplog.l('Got response from URL: ' + str(r),logtype) 

	tagstatus = "not_existing"
	if r.status_code == 200:
		tagstatus = "existing"

	fplog.l("<= out fppost, return value: tagstatus = " + str(tagstatus),logtype)

	return tagstatus

# Function to query status of fertilizer switch and set respective orange LED
#
def fertilizercheck(logtype="prod"):

	fplog.l("=> in fertilizercheck",logtype)

	input = GPIO.input(GPIO_FERTILIZER_SENSOR)

	if input:
		GPIO.output(GPIO_ORANGE_LED, GPIO.HIGH)
		fertilizer = 1
	else:
		GPIO.output(GPIO_ORANGE_LED, GPIO.LOW)
		fertilizer = 0

	fplog.l("<= out fertilizercheck, return value: fertilizer = " + str(fertilizer),logtype)

	return fertilizer
		

# Function: Phase 2 of main program flow: READ RF ID
#	
def phase2readrfid():
	
	fplog.l("PHASE2: wait for RF-ID tag")

	fertilizercheck()

	# wait for a card to be detected as present
	GPIO.output(GPIO_YELLOW_LED, GPIO.HIGH)
	fplog.l("Waiting for a card...")

	rfid.waitTag()

	fplog.l("Card is present")

	# This program expects Mifare cards
	if not rfid.readMifare():
		fplog.l("Error: The scanned RF-id tag is not a mifare card")
		abortonerror()

	# get unique ID if the card
	rfidid = rfid.getUniqueId()
	
	# overriding GLOBAL variable with local content
	global RFIDUID; RFIDUID = rfidid
	fplog.l("Card UID:" + RFIDUID)

	# wait for the card to be removed
	fplog.l("Waiting for card to be removed...")
	rfid.waitNoTag()
	fplog.l("Card removed")

	GPIO.output(GPIO_YELLOW_LED, GPIO.LOW)

	fplog.l("PHASE2: done - RF-ID tag available")

# Function: Phase 3 of main program flow: READ FLOW of WATER
#	
def phase3readwater():

	# Inititalize condition to evaluate wheter water did flow within 10 seconds or not
	nostart = True

	while nostart:

		# RF-ID leasen
		phase2readrfid()

		# Blaue LED einschalten
		GPIO.output(GPIO_BLUE_LED, GPIO.HIGH)
		fplog.l("PHASE3: Waiting for water to flow, timeout 10 seconds")
		nostart = fpflow.wfstart(10, "no")	
		if nostart:
			fplog.l("Timout kicked in, no water is flowing")
			GPIO.output(GPIO_BLUE_LED, GPIO.LOW)

	# Water is flowing, start to count the water ...

	fplog.l("Water is flowing ...")

	# Initialize counter for loop condition
	count = 11
	totalcount = 0

	while count > 10:
		count = fpflow.wfcount(0.2)
		totalcount += count
		if GPIO.input(GPIO_BLUE_LED) == 1:
			GPIO.output(GPIO_BLUE_LED, GPIO.LOW)
		else:
			GPIO.output(GPIO_BLUE_LED, GPIO.HIGH)
	
	# ovorriding GLOBAL variable with local content
	global WATERCOUNT; WATERCOUNT = totalcount

	fplog.l("Final pulses from waterflow sensor:" + str(WATERCOUNT))

	fplog.l("PHASE3: done - Amount of water available")
	GPIO.output(GPIO_BLUE_LED, GPIO.LOW)

# Function: Phase 4 of main program flow: STORE INFORMATION in WEB APPLICATION
#
def phase4storeinwebapp():

	fplog.l("PHASE4: Store information in web application")

	tagsn = RFIDUID

	fplog.l('Query for RF-ID tag: '+str(RFIDUID))
	
	# Query if tag is existing, if not, create one

	querytag = poquerytag(tagsn, "test")
	
	if querytag == "existing":
		fplog.l('Tag matches to following flower: ')
		r = requests.get(USEURL + '/flowerquery/' + str(tagsn))
		fplog.l(r.text)
		flower_hash = json.loads(r.text)
		fplog.l('The flower is a: ' + str(flower_hash["flowertype"]))

	else:
		fplog.l("Sorry, tag does not exist!")
		fplog.l("But it will try to create one")
		payload = {'tagsn': tagsn, 'pisn': PISERIAL, 'flowertype': 'new dummy', 'litershould': '0'}

		r = requests.post(USEURL + '/flowers.json', json=payload)

		if r.status_code == 201:
			fplog.l("... success in creating new flower")
			flower_hash = json.loads(r.text)
			fplog.l('The ID of the new flower is: ' + str(flower_hash["id"]))		
		else:
			fplog.l("Sorry, was not able to create a new tag")
			fplog.l('Response code is: ' + str(r.status_code))
			fplog.l('Response text is: ' + str(r.text))
			abortonerror()
			
	fplog.l("PHASE4: Tag is available (either existed or was newly created)")
	
	fertilizer = fertilizercheck()
	
	payload = {'tagsn': tagsn, 'pisn': PISERIAL, 'liter': WATERCOUNT, 'fertilizer' : fertilizer}
	r = requests.post(USEURL + '/waters.json', json=payload)

	if r.status_code == 201:
		fplog.l("... success in creating new water record")
		water_hash = json.loads(r.text)
		fplog.l('The ID of the new water is: ' + str(water_hash["id"]))		
	else:
		fplog.l("Sorry, was not able to create a new water record")
		fplog.l('Response code is: ' + str(r.status_code))
		fplog.l('Response text is: ' + str(r.text))
		abortonerror()

	blinkgreenled()

	
# ******************************************	
# START if MAIN PROGRAM
# ******************************************	

fplog.l("+++ In: flowerpi-main.py +++")

# ------------------------------------------
# Various intializations
# ------------------------------------------

# URL of web application
USEURL = 'https://immense-cliffs-8170.herokuapp.com'

# BCM (GPIO Nummern) verwenden um mit fprfid compatibel zu sein!
GPIO.setmode(GPIO.BCM)

# Set to the GPIO required to monitor the waterflow sensor (BCM notation!)
GPIO_WATERFLOW_SENSOR = 22

# GPIO_WATERFLOW_SENSOR = input => Read Pulses from Waterflow-Sensor
GPIO.setup(GPIO_WATERFLOW_SENSOR, GPIO.IN)

# Set to the GPIO required to activate the blue LED (BCM notation!)
GPIO_BLUE_LED = 7

# GPIO_BLUE_LED = output
GPIO.setup(GPIO_BLUE_LED, GPIO.OUT)
GPIO.output(GPIO_BLUE_LED, GPIO.LOW)

# Set to the GPIO required to activate the yellow LED (BCM notation!)
GPIO_YELLOW_LED = 11

# GPIO_YELLOW_LED = output
GPIO.setup(GPIO_YELLOW_LED, GPIO.OUT)
GPIO.output(GPIO_YELLOW_LED, GPIO.LOW)

# Set to the GPIO required to activate the red LED (BCM notation!)
GPIO_RED_LED = 9

# GPIO_RED_LED = output
GPIO.setup(GPIO_RED_LED, GPIO.OUT)
GPIO.output(GPIO_RED_LED, GPIO.LOW)

# Set to the GPIO required to activate the green LED (BCM notation!)
GPIO_GREEN_LED = 10

# GPIO_GREEN_LED = output
GPIO.setup(GPIO_GREEN_LED, GPIO.OUT)
GPIO.output(GPIO_GREEN_LED, GPIO.LOW)

# Set to the GPIO required to activate the orange LED (BCM notation!)
GPIO_ORANGE_LED = 5

# GPIO_ORANGE_LED = output
GPIO.setup(GPIO_ORANGE_LED, GPIO.OUT)
GPIO.output(GPIO_ORANGE_LED, GPIO.LOW)

# GPIO_FERTILIZER_SENSOR = input => Identify the state of the 'FERTILIZER' switch (on/off)
GPIO_FERTILIZER_SENSOR = 6
GPIO.setup(GPIO_FERTILIZER_SENSOR, GPIO.IN)

fertilizercheck()

# Get serial number of PI
PISERIAL = getserial()

# Define global variable for RF-ID
RFIDUID = 0

# Define global variable for counts of water
WATERCOUNT = 0

# ------------------------------------------
# PHASE1: Test if internet-connection to web-application is present
# ------------------------------------------

# Let the RED LED shine. Indication: APP is up, but looking for Internet
GPIO.output(GPIO_RED_LED, GPIO.HIGH)

while not(poquerysite()):
	fplog.l("error: " + str(USEURL) + " not accessible")
	blinkredled()
	GPIO.output(GPIO_RED_LED, GPIO.HIGH)
	time.sleep(2)

# Let the GREEN LED shine. Indication: connection to web-application established
GPIO.output(GPIO_RED_LED, GPIO.LOW)
blinkgreenled()

fplog.l("PHASE1: done - WEB-application available")

# ------------------------------------------
# PHASE2: Read RF-ID
# ------------------------------------------

# will be started below in PHASE3, in order to allow for a LOOP if not water was applied!

# ------------------------------------------
# PHASE3: Read water by means of waterflow sensor
# ------------------------------------------

phase3readwater()

# ------------------------------------------
# PHASE4: Store the amount of water applied for the flower in the WEB-application
# ------------------------------------------

fertilizercheck()

phase4storeinwebapp()
	
# ENDE des Hauptprogramms

GPIO.cleanup()

fplog.l("+++ Out: flowerpi-main.py +++")
