# Staubert 15.01.17
# Based on: https://www.modmypi.com/blog/ds18b20-one-wire-digital-temperature-sensor-and-the-raspberry-pi

import os
import time

# We then need to load our drivers. Comment Staubert - not required since already loaded on boot time via /etc/modules

# os.system('modprobe w1-gpio')
# os.system('modprobe w1-therm')

# The next step is to define our sensor’s output file (the w1_slave file) 

temp_sensor = ‘sys/bus/w1/devices/10-0008032a0b1e/w1_slave’

# We then need to define a variable for our raw temperature value (temp_raw)

def temp_raw():

    f = open(temp_sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines

# Now we read and parse the temperature

def read_temp():

    lines = temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = temp_raw()

    # Once the program is happy that the YES signal has been received, we proceed to our second line of output
    temp_output = lines[1].find('t=')

    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

# Finally, we loop our process and tell it to output our temperature data every 1 second.

while True:
        print(read_temp())
        time.sleep(1)