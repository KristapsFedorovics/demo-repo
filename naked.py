import requests
import json
import datetime
import time
import yaml

from datetime import datetime
print('Asteroid processing service')

# Initiating and reading config values
print('Loading configuration from file')

#NASA API key and  URL 
nasa_api_key = "pBHsfidaqtOPhjOogOXYrABcETVmdjESws0RQMWi"
nasa_api_url = "https://api.nasa.gov/neo/"

# Getting todays date
dt = datetime.now()
request_date = str(dt.year) + "-" + str(dt.month).zfill(2) + "-" + str(dt.day).zfill(2)  
print("Generated today's date: " + str(request_date))

#Creates API GET request using previous variables
print("Request url: " + str(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key))
r = requests.get(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key)

#prints response
print("Response status code: " + str(r.status_code))
print("Response headers: " + str(r.headers))
print("Response content: " + str(r.text))

#If HTTP status 200, parses JSON response 
if r.status_code == 200:

	json_data = json.loads(r.text)
	#Creates empty arrays
	ast_safe = []
	ast_hazardous = []
	#Check if 'element_count' exists
	if 'element_count' in json_data:
		#convert astroid count to integer
		ast_count = int(json_data['element_count'])
		print("Asteroid count today: " + str(ast_count))
		#Check if there are any astroids
		if ast_count > 0:
			#iterrate through asteroid data
			for val in json_data['near_earth_objects'][request_date]:
				#adds values  to variables
				#check if these values exists
				if 'name' and 'nasa_jpl_url' and 'estimated_diameter' and 'is_potentially_hazardous_asteroid' and 'close_approach_data' in val:
					#add values to variables
					tmp_ast_name = val['name']
					tmp_ast_nasa_jpl_url = val['nasa_jpl_url']
					#checks if 'kilometeres' exists
					if 'kilometers' in val['estimated_diameter']:
						if 'estimated_diameter_min' and 'estimated_diameter_max' in val['estimated_diameter']['kilometers']:
							#rounds diameter to three decimal points
							tmp_ast_diam_min = round(val['estimated_diameter']['kilometers']['estimated_diameter_min'], 3)
							tmp_ast_diam_max = round(val['estimated_diameter']['kilometers']['estimated_diameter_max'], 3)
						#set variables if min and max diameter don't exist
						else:
							tmp_ast_diam_min = -2
							tmp_ast_diam_max = -2
					#set variables if 'kilometers' dont exist
					else:
						tmp_ast_diam_min = -1
						tmp_ast_diam_max = -1
					#adds hazardous  status to astroid
					tmp_ast_hazardous = val['is_potentially_hazardous_asteroid']
					#if close aproach process this data
					if len(val['close_approach_data']) > 0:
						#check if these values exists in close aproach data
						if 'epoch_date_close_approach' and 'relative_velocity' and 'miss_distance' in val['close_approach_data'][0]:
							#extracts and converts date and time in seconds
							tmp_ast_close_appr_ts = int(val['close_approach_data'][0]['epoch_date_close_approach']/1000)
							tmp_ast_close_appr_dt_utc = datetime.utcfromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')
							tmp_ast_close_appr_dt = datetime.fromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')
							#if 'kilometers_per_hour' exists, extract and convert asteroid speed  to integer
							if 'kilometers_per_hour' in val['close_approach_data'][0]['relative_velocity']:
								tmp_ast_speed = int(float(val['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']))
							else:
								tmp_ast_speed = -1

							if 'kilometers' in val['close_approach_data'][0]['miss_distance']:
								tmp_ast_miss_dist = round(float(val['close_approach_data'][0]['miss_distance']['kilometers']), 3)
							else:
								tmp_ast_miss_dist = -1
						#if keys frm above block are missing, use these values
						else:
							tmp_ast_close_appr_ts = -1
							tmp_ast_close_appr_dt_utc = "1969-12-31 23:59:59"
							tmp_ast_close_appr_dt = "1969-12-31 23:59:59"
					else:
						print("No close approach data in message")
						tmp_ast_close_appr_ts = 0
						tmp_ast_close_appr_dt_utc = "1970-01-01 00:00:00"
						tmp_ast_close_appr_dt = "1970-01-01 00:00:00"
						tmp_ast_speed = -1
						tmp_ast_miss_dist = -1
					#prints the information from code above
					print("------------------------------------------------------- >>")
					print("Asteroid name: " + str(tmp_ast_name) + " | INFO: " + str(tmp_ast_nasa_jpl_url) + " | Diameter: " + str(tmp_ast_diam_min) + " - " + str(tmp_ast_diam_max) + " km | Hazardous: " + str(tmp_ast_hazardous))
					print("Close approach TS: " + str(tmp_ast_close_appr_ts) + " | Date/time UTC TZ: " + str(tmp_ast_close_appr_dt_utc) + " | Local TZ: " + str(tmp_ast_close_appr_dt))
					print("Speed: " + str(tmp_ast_speed) + " km/h" + " | MISS distance: " + str(tmp_ast_miss_dist) + " km")
					
					# Adding asteroid data to the corresponding array
					if tmp_ast_hazardous == True:
						ast_hazardous.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])
					else:
						ast_safe.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])

		else:
			print("No asteroids are going to hit earth today")
	#prints number of type of astroids
	print("Hazardous asteorids: " + str(len(ast_hazardous)) + " | Safe asteroids: " + str(len(ast_safe)))

	if len(ast_hazardous) > 0:
		#sorts hazardous astroids by time
		ast_hazardous.sort(key = lambda x: x[4], reverse=False)

		print("Today's possible apocalypse (asteroid impact on earth) times:")
		for asteroid in ast_hazardous:
			#prints possible impact times for each hazardous astroid
			print(str(asteroid[6]) + " " + str(asteroid[0]) + " " + " | more info: " + str(asteroid[1]))
		#sorts hazardous distance and prints the  distance
		ast_hazardous.sort(key = lambda x: x[8], reverse=False)
		print("Closest passing distance is for: " + str(ast_hazardous[0][0]) + " at: " + str(int(ast_hazardous[0][8])) + " km | more info: " + str(ast_hazardous[0][1]))
	else:
		print("No asteroids close passing earth today")
#if HTTP GET status not 200, gives message status
else:
	print("Unable to get response from API. Response code: " + str(r.status_code) + " | content: " + str(r.text))
