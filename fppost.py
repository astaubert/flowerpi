# A. Staubert, 11-2015
#
# This library implements the functions to interface with the Rails Application (Database) via WEB
#

import requests
import json
import fplog

USEURL = 'https://immense-cliffs-8170.herokuapp.com/'
#useurl = 'http://localhost:3000/'

# Function to query of web-site is active
#
def poquerysite(logtype="prod"):
	
	fplog.l("=> in fppost.py/poquerysite",logtype)

	fplog.l('Using URL: ' + str(USEURL),logtype) 
	r = requests.get(USEURL)
	fplog.l('Got response from URL: ' + str(r),logtype) 

	tagstatus = "False"
	if r.status_code == 200:
		tagstatus = "True"

	fplog.l("<= out fppost, return value: tagstatus = " + str(tagstatus),logtype)

	return tagstatus

# Function to query if a tag exists
#
def poquerytag(tagsn, logtype="prod"):

	fplog.l("=> in fppost.py/poquerytag",logtype)

	fplog.l('Using URL: ' + str(USEURL),logtype) 
	r = requests.get(USEURL + '/flowerquery/' + str(tagsn))
	fplog.l('Got response from URL: ' + str(r),logtype) 

	tagstatus = "not_existing"
	if r.status_code == 200:
		tagstatus = "existing"

	fplog.l("<= out fppost, return value: tagstatus = " + str(tagstatus),logtype)

	return tagstatus


# ...run automated tests if library is started as a script

if __name__ == "__main__":

	fplog.l("+++ In: fppost.py Test +++ ","test")

	poquerysite("test")

	tagsn = input('Please enter tagsn: ')

	querytag = poquerytag(tagsn, "test")
	
	if querytag == "existing":
		fplog.l('Tag matches to following flower: ',"test")
		r = requests.get(USEURL + '/flowerquery/' + str(tagsn))
		fplog.l(r.text,"test")
		flower_hash = json.loads(r.text)
		fplog.l('The flower is a: ' + str(flower_hash["flowertype"]),"test")

	else:
		fplog.l("Sorry, tag does not exist!","test")
		fplog.l("But it will try to create one","test")
		payload = {'tagsn': tagsn, 'pisn': '4711pisn', 'flowertype': 'new dummy', 'litershould': '0'}

		r = requests.post(USEURL + '/flowers.json', json=payload)

		if r.status_code == 201:
			fplog.l("... success in creating new flower","test")
			flower_hash = json.loads(r.text)
			fplog.l('The ID of the new flower is: ' + str(flower_hash["id"]),"test")		
		else:
			fplog.l("Sorry, was not able to create a new tag","test")
			fplog.l('Response code is: ' + str(r.status_code),"test")
			fplog.l('Response text is: ' + str(r.text),"test")
			
	fplog.l("+++ Goodby from: fppost.py Test +++","test")