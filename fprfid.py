# A. Staubert, 11-2015
#
# Based on:
#
# SL030 RFID tag reader example  18/08/2014  D.J.Whale
# http://blog.whaleygeek.co.uk/raspberry-pi-rfid-tag-reader
#
# For use with SKPang Electronics SL030 RFID module,
# with a SL030 Raspberry Pi cable, and a Raspberry Pi
# running Raspbian Wheezy.
# product numbers: RFID-SL030, RSP-SL030-CAB
# http://skpang.co.uk/blog/archives/946
#
# Run this program as follows:
#   sudo python fprfid.py

import RPi.GPIO as GPIO

# Import this module to gain access to the RFID driver
import rfid

# Import this module for generic logging used in flowerpi project
import fplog

# Set to the GPIO required to activate the yellow LED (BCM notation!)
# GPIO_YELLOW_LED = 11
# 07.01.17 commented-out because duplicate - see flowerpi-main.py


# ...run automated tests if library is started as a script

if __name__ == "__main__":
	fplog.l("+++ In: fprfid.py Test +++ ","test")

        # GPIO_YELLOW_LED = output => Ansteuerung der gelben LED = Warten auf TAG
    	GPIO.setup(GPIO_YELLOW_LED, GPIO.OUT)

	while True:

	  # wait for a card to be detected as present
	  GPIO.output(GPIO_YELLOW_LED, GPIO.HIGH)
	  fplog.l("Waiting for a card...","test")

	  rfid.waitTag()

	  fplog.l("Card is present","test")
	  GPIO.output(GPIO_YELLOW_LED, GPIO.LOW)

	  # This demo only uses Mifare cards
	  if not rfid.readMifare():
	    fplog.l("This is not a mifare card","test")
	  else:
	    # What type of Mifare card is it? (there are different types)
	    fplog.l("Card type:" + rfid.getTypeName(),"test")

	    # get unique ID if the card
	    uid = rfid.getUniqueId()
	    fplog.l("Card UID:" + uid,"test")

	  # wait for the card to be removed
	  fplog.l("Waiting for card to be removed...","test")
	  rfid.waitNoTag()
	  fplog.l("Card removed","test")

# END
