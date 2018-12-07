import time, random, gspread, urllib.request, re, datetime
from oauth2client.service_account import ServiceAccountCredentials
import bs4 as bs

from config import GoogleSheets

# Types of cars to scrape [Eco Sport; F-150; Escape]
# Things to scrape: Price/ Discounts
		
################ FEATURE #1 - Pulling all inventory from the same page
def inventoryLevels():
	targetPage = urllib.request.urlopen('http://www.vickarford.ca/en/new-inventory')
	soup = bs.BeautifulSoup(targetPage,'lxml')

	listOfCars1 = soup.find_all("ul", "nav-block__navigation-list ")[1]
	listOfCars2 = listOfCars1.find_all('span')

	# Below code extracts all inventory levels for all cars
	listOfCars4 =[]
	for unfilteredList in listOfCars2:
		listOfCars2 = unfilteredList.text.replace("\n","").replace(" ","").replace("(","").replace(")","")
		listOfCars4.append(listOfCars2)

	carModels = []
	carInventory = []
	for index in range(len(listOfCars4)):
		if index % 2 == 0:
			carModels.append(listOfCars4[index])
		else:
			carInventory.append(listOfCars4[index])

	# print(carModels)
	# print(carInventory)

	return(carModels,carInventory)

################ FEATURE #2 - Extracting all car references

def urlExtraction():
	targetPage = urllib.request.urlopen('http://www.vickarford.ca/en/new-inventory')
	soup = bs.BeautifulSoup(targetPage,'lxml')

	listOfCars1 = soup.find_all("ul", "nav-block__navigation-list ")[1]
	listOfCars2 = listOfCars1.find_all('span')

	urlForAllCars = []
	for url in listOfCars1.find_all('a'):
		urlForAllCars.append(url.get('href'))

	return(urlForAllCars)

	#The below is for testing purposes
	# link=['en/new-inventory/ford/e-series_cutaway']
	# return(link)

####################################################################################################################################

################ FEATURE #3 - Getting all types of cars and prices (Ecosport)

def priceSearch(listOfFullLinks):

	googleSheetPopulateDetails(['Timestamp: {:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now())])
	#/en/new-inventory/ford/e-series_cutaway
	for listOfLinks in listOfFullLinks:
		# Throwing a try event here as "if statement" to loop through the pages to be mined.
		try:
			carModelName3 = ["Trims"]
			carModelFullPrice3 = ["Before Price ($)"]
			carModelDiscountedPrice3 = ["Current Price ($)"]
			discountRatio = ["Discount Ratio"]

			index = 1
			while True:
				print('\n\n'+ '********'+listOfLinks)
				sauce = urllib.request.urlopen('http://www.vickarford.ca/' + str(listOfLinks) + '?limit=200&page=' + str(index))
				#Parsing tool lxml
				soup = bs.BeautifulSoup(sauce,'lxml')

				######## Sub - Model Names - Minifeature

				#targeting main div that contains the FULL PRICE / refer to HTML if you need to see wheere the below is
				carModelName = soup.find_all("a", "inventory-list-layout__preview-name")[0]
				carModelName2 = soup.find_all("strong")
				for eachName in carModelName2:
					#cleaning the data with the line below
					carModelName3.append(eachName.text.replace("\n","").replace(" ",""))

				######## After Discount Price - Minifeature

				#targeting main div that contains the After Discount Price / refer to HTML if you need to see wheere the below is
				carModelDiscountedPrice = soup.find_all("div", "inventory-list-layout__preview-price-current")
				carModelDiscountedPrice2 = soup.find_all("b")[2:]
				for eachName in carModelDiscountedPrice2:
					#cleaning the data with the line below
					carModelDiscountedPrice3.append(eachName.text.replace("\n","").replace(" ",""))

				######## Full-Price - Minifeature

				#targeting main div that contains the FULL PRICE / refer to HTML if you need to see wheere the below is

				carModelFullPrice = soup.find_all("article", "inventory-list-layout")
				for items in carModelFullPrice:
				 	if items.find("del") != None:
				 		carModelFullPrice3.append(items.find("del").text)
				 	else:
				 		carModelFullPrice3.append("$0")

				carModelFullPrice3

				########################

				#Adds $0 to the cell if there is no before price
				if len(carModelFullPrice3) == 1:
					for i in range(len(carModelDiscountedPrice3)-1):
						carModelFullPrice3.append("$0")

				carModelFullPrice3 = carModelFullPrice3

				####### Discount ratio

				#Only activate if there was a previous full price to compare the discount, else it will populate it as 0
				if carModelFullPrice3[1] != "$0":
					x = carModelDiscountedPrice3[1:]
					for j,i in enumerate(x):
						x[j] = int(x[j].replace("$","").replace(",",""))

					y = carModelFullPrice3[1:]
					for j,i in enumerate(y):
						y[j] = int(y[j].replace("$","").replace(",",""))

					discountRatio1 = [a - b for a, b in zip(x, y)]
					
					for j,i in enumerate(discountRatio1):
						discountRatio1[j] = "$" + str(discountRatio1[j])
					discountRatio.extend(discountRatio1)
				else:
					if len(discountRatio) == 1:
						for i in range(len(carModelDiscountedPrice3)-1):
							discountRatio.append("$0")

				#Fixing bug of having more discount fields than cars aka empty fields showing discounts prices
				if len(carModelFullPrice3) < len(discountRatio):
					approriateLength = len(carModelFullPrice3) - len(discountRatio)
					discountRatio = discountRatio [:approriateLength]

				# Prints below to see results

				print('This is the length of above for carModelName3 = ' + str(len(carModelName3)))
				print(carModelName3)
				googleSheetPopulateDetails(carModelName3)
				time.sleep(random.uniform(1,3))

				print('This is the length of above for carModelFullPrice3 = ' + str(len(carModelFullPrice3)))
				print(carModelFullPrice3)
				googleSheetPopulateDetails(carModelFullPrice3)
				time.sleep(random.uniform(1,3))

				print('This is the length of above for carModelDiscountedPrice3 = ' + str(len(carModelDiscountedPrice3)))
				print(carModelDiscountedPrice3)
				googleSheetPopulateDetails(carModelDiscountedPrice3)
				time.sleep(random.uniform(1,3))

				print('This is the length of above for discountRatio = ' + str(len(discountRatio)))
				print(discountRatio)
				googleSheetPopulateDetails(discountRatio)
				time.sleep(random.uniform(1,3))

				googleSheetPopulateDetails(["."])

				index = index +1
		except Exception as e:
			print('ERROR on the scraping process: ' + str(e))
			print("Ran out of pages")
		# print(carModelFullPrice3)

	# return carModelName3,carModelFullPrice3,carModelDiscountedPrice3

################ FEATURE #4 - Migrating data to google drive/ GSheets

def googleSheetPopulate(inventoryNames, inventoryQty):

	scope = [GoogleSheets.scope_1, GoogleSheets.scope_2]
	credentials = ServiceAccountCredentials.from_json_keyfile_name('test1-4ece2aa60b8c.json', scope)

	gc = gspread.authorize(credentials)

	######################################
	#Moving inventory data to google sheets
	wks = gc.open('Vickarford Inventory and Price Analysis')

	wks1 = wks.worksheet("INVENTORY_DATA_RAW")

	wks1.update_acell('A1', 'Timestamp: {:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()))

	# Below code is to obtain size of the row, as the inventory may increase or d

	dictionary = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h',9: 'i', 10: 'j', 11: 'k', 12: 'l', 13: 'm', 14: 'n', 15: 'o', 16: 'p',17: 'q', 18: 'r', 19: 's', 20: 't', 21: 'u', 22: 'v', 23: 'w', 24: 'x',25: 'y', 26: 'z', 27: 'aa', 28: 'ab', 29: 'ac', 30: 'ad', 31: 'ae', 32: 'af', 33: 'ag', 34: 'ah', 35: 'ai', 36: 'aj', 37: 'ak', 38: 'al', 39: 'am', 40: 'an', 41: 'ao', 42: 'ap', 43: 'aq', 44: 'ar', 45: 'as', 46: 'at', 47: 'au', 48: 'av', 49: 'aw', 50: 'ax', 51: 'ay', 52: 'az', 53: 'ba', 54: 'bb', 55: 'bc', 56: 'bd', 57: 'be', 58: 'bf', 59: 'bg', 60: 'bh', 61: 'bi', 62: 'bj', 63: 'bk', 64: 'bl', 65: 'bm', 66: 'bn', 67: 'bo', 68: 'bp', 69: 'bq', 70: 'br', 71: 'bs', 72: 'bt', 73: 'bu', 74: 'bv', 75: 'bw', 76: 'bx', 77: 'by', 78: 'bz', 79: 'ca', 80: 'cb', 81: 'cc', 82: 'cd', 83: 'ce', 84: 'cf', 85: 'cg', 86: 'ch', 87: 'ci', 88: 'cj', 89: 'ck', 90: 'cl', 91: 'cm', 92: 'cn', 93: 'co', 94: 'cp', 95: 'cq', 96: 'cr', 97: 'cs', 98: 'ct', 99: 'cu', 100: 'cv', 101: 'cw', 102: 'cx', 103: 'cy', 104: 'cz', 105: 'da', 106: 'db', 107: 'dc', 108: 'dd', 109: 'de', 110: 'df', 111: 'dg', 112: 'dh', 113: 'di', 114: 'dj', 115: 'dk', 116: 'dl', 117: 'dm', 118: 'dn', 119: 'do', 120: 'dp', 121: 'dq', 122: 'dr', 123: 'ds', 124: 'dt', 125: 'du', 126: 'dv', 127: 'dw', 128: 'dx', 129: 'dy', 130: 'dz', 131: 'ea', 132: 'eb', 133: 'ec', 134: 'ed', 135: 'ee', 136: 'ef', 137: 'eg', 138: 'eh', 139: 'ei', 140: 'ej', 141: 'ek', 142: 'el', 143: 'em', 144: 'en', 145: 'eo', 146: 'ep', 147: 'eq', 148: 'er', 149: 'es', 150: 'et', 151: 'eu', 152: 'ev', 153: 'ew', 154: 'ex', 155: 'ey', 156: 'ez', 157: 'fa', 158: 'fb', 159: 'fc', 160: 'fd', 161: 'fe', 162: 'ff', 163: 'fg', 164: 'fh', 165: 'fi', 166: 'fj', 167: 'fk', 168: 'fl', 169: 'fm', 170: 'fn', 171: 'fo', 172: 'fp', 173: 'fq', 174: 'fr', 175: 'fs', 176: 'ft', 177: 'fu', 178: 'fv', 179: 'fw', 180: 'fx', 181: 'fy', 182: 'fz'}
	inventoryNamesLenght = dictionary[len(inventoryNames)]
	rang1 = 'A2:' + str(inventoryNamesLenght) + str(2)

	cell_list = wks1.range(rang1)
	index = 0
	for cell in cell_list:
		cell.value = inventoryNames[index]
		index = index +1
	# Update in batch
	wks1.update_cells(cell_list, 'USER_ENTERED')

	inventoryQtyLenght = dictionary[len(inventoryQty)]
	rang2 = 'A3:' + str(inventoryNamesLenght) + str(3)

	cell_list = wks1.range(rang2)
	index = 0
	for cell in cell_list:
		cell.value = inventoryQty[index]
		index = index +1
	# Update in batch
	wks1.update_cells(cell_list, 'USER_ENTERED')

#########################################
def googleSheetPopulateDetails(x):
	print("append google sheets")
	scope = [GoogleSheets.scope_1, GoogleSheets.scope_2]
	credentials = ServiceAccountCredentials.from_json_keyfile_name('test1-4ece2aa60b8c.json', scope)

	gc = gspread.authorize(credentials)
	
	wks = gc.open('Vickarford Inventory and Price Analysis').worksheet("PRICE_DATA_RAW")

	wks.append_row(x, 'USER_ENTERED')

#########################################
def clearGoogleSheet():
	scope = [GoogleSheets.scope_1, GoogleSheets.scope_2]
	credentials = ServiceAccountCredentials.from_json_keyfile_name('test1-4ece2aa60b8c.json', scope)
	gc = gspread.authorize(credentials)

	wks = gc.open('Vickarford Inventory and Price Analysis').worksheet("PRICE_DATA_RAW")
	range_of_cells = wks.range('A1:ZZ200')
	for cell in range_of_cells:
	    cell.value = ''
	wks.update_cells(range_of_cells) 
	time.sleep(4)

####################################################################################################################################

################ MAIN CONTROL PANEL
def main():
	clearGoogleSheet()
	inventoryNames, inventoryQty = inventoryLevels()
	googleSheetPopulate(inventoryNames, inventoryQty)
	listOfFullLinks = urlExtraction()
	detailCarData = priceSearch(listOfFullLinks)

main()

####################################################################################################################################
