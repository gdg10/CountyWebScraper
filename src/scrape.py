from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import csv, io, datetime, copy, os, sys

YEARS = 10
COUNTY_LIST= ["ALLEN TOWNSHIP","BANGOR BOROUGH","BATH BOROUGH","BETHLEHEM CITY",
"BETHLEHEM TOWNSHIP","BUSHKILL TOWNSHIP","CHAPMAN BOROUGH","EAST ALLEN TOWNSHIP",
"EAST BANGOR BOROUGH","EASTON CITY","FORKS TOWNSHIP","FREEMANSBURG BOROUGH","GLENDON BOROUGH",
"HANOVER TOWNSHIP","HELLERTOWN BOROUGH","LEHIGH TOWNSHIP","LOWER MT BETHEL TOWNSHIP",
"LOWER NAZARETH TOWNSHIP","LOWER SAUCON TOWNSHIP","MOORE TOWNSHIP","N CATASAUQUA BOROUGH",
"NAZARETH BOROUGH","NORTHAMPTON BOROUGH","PALMER TOWNSHIP","PEN ARGYL BOROUGH","PLAINFIELD TOWNSHIP",
"PORTLAND BOROUGH","ROSETO BOROUGH","STOCKERTOWN BOROUGH","TATAMY BOROUGH","UPPER MT BETHEL TOWNSHIP",
"UPPER NAZARETH TOWNSHIP","WALNUTPORT BOROUGH","WASHINGTON TOWNSHIP","WEST EASTON BOROUGH",
"WILLIAMS TOWNSHIP","WILSON BOROUGH","WIND GAP BOROUGH"]
DATA_HEADER = "Parcel|Address|Date|Price|dc1|dc2|Use|dc3\n"
LOW_PRICE = 25000
HIGH_PRICE =500000

def getParams():		#retrieve time frame"," and municipality from user

	print("\nMunicipality Selection")	#get municipality input
	for i in range (len(COUNTY_LIST)):
		print(str(i)+". " + COUNTY_LIST[i])
	print("\nEnter the number of the municipality you'd like to search: ")
	mNum = int(input())

	print("\nDuration Selection")	#choose search duration
	print("1. Last "+ str(YEARS) + " Years\n2. Custom Search \n\nEnter search duration selection: ")
	durSelection = int(input())
	if durSelection == 1:									# Generate ten year span
		now = datetime.datetime.now()						# Get current date
		startDate = now - datetime.timedelta(days=365*YEARS)# Subtract x years
		endDate = now.strftime("%m/%d/%Y")					# Format for county site	
		startDate = startDate.strftime("%m/%d/%Y")			# Format for county site
	elif durSelection == 2:									# Get time period from user
		print("Enter the search START DATE")
		startDate = ObtainDate()
		print("Enter the search END DATE (within 6 months of START DATE)")
		endDate = ObtainDate()

	return [mNum, startDate, endDate]

def autoParams():
	now = datetime.datetime.now()						# Get current date
	startDate = now - datetime.timedelta(days=365*YEARS)# Subtract x years
	endDate = now.strftime("%m/%d/%Y")					# Format for county site	
	startDate = startDate.strftime("%m/%d/%Y")			# Format for county 

	startDate = datetime.datetime.strptime(startDate, "%m/%d/%Y")	# Create dateTime objects from input date strings
	endDate = datetime.datetime.strptime(endDate, "%m/%d/%Y")	
	sixMonths = datetime.timedelta(days=182)						# Create six month delta
	oneDay = datetime.timedelta(days=1)								# Create a single day delta
	dateList = []													# Create a list of all start/end dates to return

	while(startDate + sixMonths < endDate):			# Split into 6 month increments by looping
		dateList.append(copy.deepcopy(startDate))	# append copy(startdate) to list
		startDate = startDate + sixMonths			# start date = start date + six months
		dateList.append(copy.deepcopy(startDate))	# append copy(startdate) to list 
		startDate = startDate + oneDay				# start date = start date + 1 day 
	dateList.append(copy.deepcopy(startDate))		# append to list
	dateList.append(endDate)						# append endDate to list
	
	for i in range(len(dateList)):					# stringify all dates
		dateList[i] = dateList[i].strftime("%m/%d/%Y")

	return dateList


def scrape(mNum, startDate, endDate):
	print("\t--> querying from " + startDate + " to " + endDate)

	#open browser and go to website
	driver = webdriver.Chrome()
	driver.get("https://www.ncpub.org/_web/search/advancedsearch.aspx?mode=sales")

	#accept terms agreement
	elem = driver.find_element_by_name("btAgree")
	elem.click()

	#select drop down menu and select Sales Date
	crit = driver.find_element(By.XPATH, '//*[@id="sCriteria"]')
	critDropDown = Select(crit)
	critDropDown.select_by_index(5)

	# select "From:"" field
	elem = driver.find_element(By.XPATH, '//*[@id="ctl01_cal1_dateInput"]')
	elem.send_keys(startDate)

	#selec "To:" field
	elem = driver.find_element(By.XPATH, '//*[@id="ctl01_cal2_dateInput"]')
	elem.send_keys(endDate)

	#click "Add" button
	elem = driver.find_element(By.XPATH, '//*[@id="btAdd"]')
	elem.click()

	#select drop down menu and select Sale Amount
	crit = driver.find_element(By.XPATH, '//*[@id="sCriteria"]')
	critDropDown = Select(crit)
	critDropDown.select_by_index(4)

	# select "From:"" field
	elem = driver.find_element(By.XPATH, '//*[@id="txtCrit"]')
	elem.send_keys(LOW_PRICE)

	#selec "To:" field
	elem = driver.find_element(By.XPATH, '//*[@id="txtCrit2"]')
	elem.send_keys(HIGH_PRICE)

	#click "Add" button
	elem = driver.find_element(By.XPATH, '//*[@id="btAdd"]')
	elem.click()

	#select criteria drop down menu and select Municipality
	crit = driver.find_element(By.XPATH, '//*[@id="sCriteria"]')
	critDropDown = Select(crit)
	critDropDown.select_by_index(2)

	#select municipality drop down menu and select a municipality
	muni = driver.find_element(By.XPATH, '//*[@id="sPickList"]')
	muniDropDown = Select(muni)
	muniDropDown.select_by_index(mNum)

	#click "Add" button
	elem = driver.find_element(By.XPATH, '//*[@id="btAdd"]')
	elem.click()

	#select results/page dropdown and pick max val
	crit = driver.find_element(By.XPATH, '//*[@id="selPageSize"]')
	critDropDown = Select(crit)
	critDropDown.select_by_index(4)

	#click "Search" button
	elem = driver.find_element(By.XPATH, '//*[@id="btSearch"]')
	elem.click()

	# fileName = str(mNum) + "_" + str(startDate) + "_" + str(endDate) + "_.csv"		#TODO: dynamically create output file name off of search params
	with io.open(COUNTY_LIST[mNum] + ".csv", mode="a+", errors="replace") as outputFile:
		try:
			#scrape table of info, then get next page
			count = 1
			while count < 11:
				
				#scrape entire results table
				elem = driver.find_element(By.XPATH, '//*[@id="searchResults"]/tbody')
				print("\t\t--> scraping results page: " + str(count))
				#print(elem.text)
				
				#for each row in the table grab data, and also grab deepData
				sData = elem.text.split("\n")
				rows = len(sData)/7
				for x in range(rows):
					#perform some basic data cleanup
					if x == 0:						#don't write header row ever
						print("\t\t\t(Header row ommitted)")
					else:
						driver, deepData = getDeepData(driver, x)#navigate deep and then come back
						row = sData[x*7] + "| " + sData[x*7 + 1]+ "| " + sData[x*7 + 2]+ "| " + sData[x*7 + 3]+ "| " + sData[x*7 + 4]+ "| " + sData[x*7 + 5]+ "| " + sData[x*7 + 6]+ "| " + deepData[0]+ "| " + deepData[1]+ "| " +"\n"
						strRow = str(row)
						intPrice = int(str(sData[x*7 + 3])[1:-3].replace(',', ''))	#cast from unicode to string, slice off '$' and '.00', remove commas, then cast to int
						if strRow.find("Resi") == -1:
							print("\t\t\t(non residential property omitted)")
						elif intPrice < LOW_PRICE or intPrice > HIGH_PRICE:
							print("\t\t\t(Sale outside configured $" + str(LOW_PRICE) + "-$"+ str(HIGH_PRICE) +" price range omitted)")
						else:
							outputFile.write(row.decode('utf-8'))		#write data
				#print(elem.text)
				
				#iterate
				count = count + 1
				
				#search for next page button, its location changes
				if count < 11:
					index = getNextPageIndex(driver)
				if index == None:
					#finished
					break
				else:
					elem = driver.find_element_by_xpath('//*[@id="frmMain"]/table/tbody/tr/td/div/div/table[2]/tbody/tr/td[1]/table/tbody/tr[3]/td/center/table[3]/tbody/tr/td[2]/font[2]/a[' + str(index) + ']')
					elem.click()
		except:
			print("\t\t--> no results")
			print("\nPossibly unexpected error:", sys.exc_info()[0])

	driver.close()	#close the browser
	return 1

def ObtainDate():
    isValid=False
    while not isValid:
        userIn = raw_input("Type Date mm/dd/yyyy: ")
        try: # strptime throws an exception if the input doesn't match the pattern
            d = datetime.datetime.strptime(userIn, "%m/%d/%Y")
            isValid=True
        except:
            print("Doh, try again!\n")
    return userIn

def getNextPageIndex(driver):
	i = 1
	while i < 12:
		try:
			elem = driver.find_element_by_xpath('//*[@id="frmMain"]/table/tbody/tr/td/div/div/table[2]/tbody/tr/td[1]/table/tbody/tr[3]/td/center/table[3]/tbody/tr/td[2]/font[2]/a[' + str(i) + ']')
			if elem.text == ' Next >>':
					# print("the correct i is: " + str(i))
					return i;
			else:
				# print("wrong i: " + str(i))
				i = i+1
		except:
			#print("End of scrape data")	# aka: cannot find Next button
			return None

def splitDate(startDate, endDate):
	startDate = datetime.datetime.strptime(startDate, "%m/%d/%Y")	# Create dateTime objects from input date strings
	endDate = datetime.datetime.strptime(endDate, "%m/%d/%Y")	
	sixMonths = datetime.timedelta(days=182)						# Create six month delta
	oneDay = datetime.timedelta(days=1)								# Create a single day delta
	dateList = []													# Create a list of all start/end dates to return

	while(startDate + sixMonths < endDate):			# Split into 6 month increments by looping
		dateList.append(copy.deepcopy(startDate))	# append copy(startdate) to list
		startDate = startDate + sixMonths			# start date = start date + six months
		dateList.append(copy.deepcopy(startDate))	# append copy(startdate) to list 
		startDate = startDate + oneDay				# start date = start date + 1 day 
	dateList.append(copy.deepcopy(startDate))		# append to list
	dateList.append(endDate)						# append endDate to list
	
	for i in range(len(dateList)):					# stringify all dates
		dateList[i] = dateList[i].strftime("%m/%d/%Y")

	return dateList

def getDeepData(driver, x):
	
	yearBuilt = 0			
	squareFootage = 0
	
	# search for year built and sqrft. Return 0's if error.
	try:	
		elem = driver.find_element(By.XPATH, '//*[@id="searchResults"]/tbody/tr['+str(2+x)+']/td[2]/div')
		elem.click()	#click first table result

		elem = driver.find_element(By.XPATH, '//*[@id="sidemenu"]/li[4]/a/span')
		elem.click()	#click residential tab

		try:
			elem = driver.find_element(By.XPATH, '//*[@id="Residential"]/tbody/tr[7]/td[2]')
			squareFootage = elem.text	#copy sqaure footage
			# print("Square footage: " + squareFootage)
		except:
			#no data available
			print("\t\t\t(Square footage not available)")

		try:
			
			elem = driver.find_element(By.XPATH, '//*[@id="Residential"]/tbody/tr[3]/td[2]')
			yearBuilt = elem.text	#copy year built
			# print("Year built: " + yearBuilt)
		except:
			print("\t\t\t(Year built not available)")

		elem = driver.find_element(By.XPATH, '//*[@id="ml"]')	
		elem.click()	#click "return to search results"
	except:
		print("\t\t\t(Deep search error)")

	deepData = [str(yearBuilt), str(squareFootage)]
	return driver, deepData

def createOutputFile(muni):
	print("Checking for old output file")							# Remove old output file if it exists
	path = str(COUNTY_LIST[muni]) + ".csv"
	exists = os.path.isfile(path)
	if exists:
		print("\nRemoving old output file")	
		os.remove(COUNTY_LIST[muni] + ".csv")	

	print("\nCreating output file in current directory")			# Create new output file and add header
	with io.open(COUNTY_LIST[muni] + ".csv", mode="a+", errors="replace") as outputFile:
		outputFile.write(DATA_HEADER.decode('utf-8'))				# Write header to file

if __name__ == "__main__":
	
	if len(sys.argv) != 2:
		print("\nMust use 'man' or 'auto' parameter\nusage: python scrape.py [man/auto]\n")
		sys.exit(1)

	elif sys.argv[1] == "auto":
		dateList = autoParams()								# Gen date list only once 
		
		for k in range(len(COUNTY_LIST)):					# Loop through all municipalities
			createOutputFile(k) 							# Delete old output file, make a new one, add data header
			j = 0	
			print("\nSearching " + COUNTY_LIST[k] + " public tax records: ")												
			for i in range(len(dateList)/2):
				scrape(k, dateList[j], dateList[j+1])		# Perform scrapes
				j = j+2

	elif sys.argv[1] == "man":
		scrapeParams = getParams();									# Get search params from user
		dateList = splitDate(scrapeParams[1], scrapeParams[2])		# Split search date into 6 months increments if needed
		createOutputFile(scrapeParams[0]);							# delete old output file, make a new one, add data header
		
		j = 0	
		print("\nSearching " + COUNTY_LIST[scrapeParams[0]] + " public tax records from " + str(scrapeParams[1]) + " till " + str(scrapeParams[2]) + ": ")												
		for i in range(len(dateList)/2):
			scrape(scrapeParams[0], dateList[j], dateList[j+1])		# Perform scrapes
			j = j+2

	else:
		print("\nMust use 'man' or 'auto' parameter\nusage: python scrape.py [man/auto]\n")
		sys.exit(1)

	print("\nCompleted\n\n")
	sys.exit(0)
