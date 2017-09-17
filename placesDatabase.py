import sqlite3
from googleplaces import GooglePlaces, types, lang
import time

GMAPS_API_KEY = 'AIzaSyCPL0mX8XkQC_5UIlx_caVj-TyXsj-yDVo'

create_table_sql = """ CREATE TABLE IF NOT EXISTS places (
                                        id BLOB NOT NULL PRIMARY KEY UNIQUE,
                                        latitude REAL NOT NULL,
                                        longitude REAL NOT NULL,
                                        style BLOB
                                    ); """

"""try:
    conn = sqlite3.connect('databases/places.db')
    c = conn.cursor()
    c.execute(create_table_sql)
except Error as e:
    print(e)"""


def storePlace(place, style, timestamp):
	conn = sqlite3.connect('databases/places.db')
	c = conn.cursor()

	#Check if the place is already added
	c.execute("SELECT id FROM places WHERE id = ?", (place.place_id,))
	dbPlace = c.fetchone()
	if(dbPlace != None):
		#The place is already added
		conn.close()
		return

	print(place.name)
	t = (place.place_id, float(place.geo_location['lat']), float(place.geo_location['lng']), style, timestamp)
	c.execute("INSERT INTO places VALUES (?, ?, ?, ?, ?)", t)
	conn.commit()
	conn.close()
	
	return

def getPlacesAtPointFromGMaps(latitude, longitude):
	google_places = GooglePlaces(GMAPS_API_KEY)
	query_result = google_places.nearby_search(
	        location= str(latitude)+', '+str(longitude), keyword='',
	        radius=1000, types=[types.TYPE_NIGHT_CLUB])
	#Max radius = 50,000m
	#Types to use: cafe, casino, night_club

	for place in query_result.places:
		# Returned places from a query are place summaries.
		storePlace(place, '', -1)

	while query_result.has_next_page_token:
		print("\n")
		time.sleep(3)
		query_result = google_places.nearby_search(
	            pagetoken=query_result.next_page_token)

		for place in query_result.places:
			storePlace(place, '', -1)

def getPlaceLocation(placeId):
	#Check if place exists and get location
	conn = sqlite3.connect('databases/places.db')
	c = conn.cursor()

	#Check if the place is already added
	c.execute("SELECT latitude, longitude FROM places WHERE id = ?", (placeId,))
	dbPlace = c.fetchone()
	if(dbPlace == None):
		#The place is already added
		conn.close()
		return None

	lat = dbPlace[0]
	lng = dbPlace[1]

	conn.close()
	return (lat, lng)

#getPlacesAtPointFromGMaps(40.427491, -3.700221)