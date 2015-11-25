# A. Staubert, 11-2015
#
# This library implements the genering loggin function "l" to be used with the flowerpi-python-project
#
# 3 logtypes are possible: no, prod (production) [default], test
#

import datetime

# Function to create standardaized log entries
#
def l(value, logtype="prod"):
	stamp = str(datetime.datetime.now()).split('.')[0]
	logstring = "fplog " + stamp + ": " + str(value)
	
	if str(logtype) == "prod" or str(logtype) == "test":
		print logstring
	
	if str(logtype) == "prod":
		myfile = open("flowerpi_prod.log", "a")
		myfile.write(logstring)
		myfile.write("\n")
		myfile.close()

	if str(logtype) == "test":
  		myfile = open("flowerpi_test.log", "a")
  		myfile.write(logstring)
		myfile.write("\n")
		myfile.close()


# ...run automated tests if library is started as a script

if __name__ == "__main__":
  l("+++ In: fpflow.py Test +++ ","test")
  l("Log to production","test")
  l("No log","no")
  l("+++ Goodby from: fplog.py Test +++","test")
