import sqlite3
import time
import numpy as np
from threading import Thread
#import reverse_geocoder as rg
#https://github.com/thampiman/reverse-geocoder for getting city and country
#sudo apt-get install python-numpy python-scipy
#sudo pip install reverse_geocoder
import utils
import dbscan
import placesDatabase as placesDB

#Distance in meters
minDist = 20
minPoints = 10

#public in database: 0=hidden 1=public for friends, 2=everybody

def storePlacesIdArroundUser(latitude, longitude):
	conn = sqlite3.connect('databases/locations.db')
	c = conn.cursor()

	#Get the points around aprox 110 m each side
	maxLat = latitude + 0.001
	minLat = latitude - 0.001
	maxLng = longitude + 0.001
	minLng = longitude - 0.001

	timestamp = utils.timeInMillis()
	#Update every month (30 days)
	pastTS = timestamp - 30* 24 * 60 * 60 * 1000

	t = (pastTS, maxLat, minLat, maxLng, minLng)
	c.execute("""SELECT id
        FROM locations
        WHERE timestamp >= ?
        AND latitude <= ? AND latitude >= ? AND longitude <= ? AND longitude >= ?""", t)


	#Update / get the places in a separate thread
	thread = Thread(target = placesDB.getPlacesAtPointFromGMaps, args = (latitude, longitude))
	thread.start()


def postUserLocation(name, latitude, longitude, public):
	#0 = OK, 1 = Wrong user name,
	conn = sqlite3.connect('databases/locations.db')
	c = conn.cursor()

	#Check if the username exist
	#TODO do a real login. We'd need to store the password on the phone
	#login = userDB.userSignIn(name, pass)

	#Store the location
	#TODO, calculate the city and the country for faster searches
	timestamp = utils.timeInMillis()

	t = (name, latitude, longitude, timestamp, "country1", "city1", public)
	c.execute("INSERT INTO locations(user, latitude, longitude, timestamp, country, city, public) VALUES (?, ?, ?, ?, ?, ?, ?)", t)
	conn.commit()

	conn.close()

	storePlacesIdArroundUser(latitude, longitude)

	return 0

def getUserLocationMap(name, latitude, longitude):
	userMap = []
	conn = sqlite3.connect('databases/locations.db')
	c = conn.cursor()

	timestamp = utils.timeInMillis()
	#Use just the last 30 minutes of data
	pastTS = timestamp - 30 * 60 * 1000
	#Get the points around aprox 1,1 km each side
	maxLat = latitude + 0.01
	minLat = latitude - 0.01
	maxLng = longitude + 0.01
	minLng = longitude - 0.01

	t = (name, pastTS, maxLat, minLat, maxLng, minLng)

	resultPoints = c.execute("""SELECT latitude, longitude,
        MAX(timestamp) AS timestamp
        FROM locations
        WHERE user != ? AND timestamp >= ?
        AND latitude <= ? AND latitude >= ? AND longitude <= ? AND longitude >= ?
        GROUP BY user""", t)

	latitudeStr = ''
	longitudeStr = ''

	for row in resultPoints:
		latitudeStr += ' ' + str(row[0])
		longitudeStr += ' ' + str(row[1])

	m = np.matrix(latitudeStr +';'+longitudeStr)
    
	dbscanResult = dbscan.dbscan(m, minDist, minPoints)
	#print('dbscan: \n'+str(dbscanResult)+'\n\n')

	for clusterPoint in dbscanResult:
		print(clusterPoint)
		#Get the places arround
		placesConn = sqlite3.connect('databases/places.db')
		placesC = placesConn.cursor()
		radius = utils.getRadius(clusterPoint[2])

		deltaRad = 0.0004 * radius #0.00001 = 1.1m
		maxLat = clusterPoint[0] + deltaRad
		minLat = clusterPoint[0] - deltaRad
		maxLng = clusterPoint[1] + deltaRad
		minLng = clusterPoint[1] - deltaRad

		t = (maxLat, minLat, maxLng, minLng)
		placesArround = placesC.execute("SELECT id, latitude, longitude FROM places WHERE latitude <= ? AND latitude >= ? AND longitude <= ? AND longitude >= ?", t)
		places = []
		for row in placesArround:
			print("\t"+str(row))
			place = utils.setUpGMapPlace(row[0], row[1], row[2])
			places.append(place)

		if len(places) > 0 : 
			point = utils.setUpPoint(clusterPoint[0], clusterPoint[1], radius, places)
			userMap.append(point)

		placesConn.close()

	conn.close()
	return userMap

def getUsersArround(lat, lng, radius, timestamp):
	conn = sqlite3.connect('databases/locations.db')
	c = conn.cursor()


	#1.1m * radius
	maxLat = lat + 0.00001 * radius
	minLat = lat - 0.00001 * radius
	maxLng = lng + 0.00001 * radius
	minLng = lng - 0.00001 * radius
	t = (timestamp, maxLat, minLat, maxLng, minLng)

	users = c.execute("""SELECT user,
        MAX(timestamp) AS timestamp
        FROM locations
        WHERE timestamp >= ?
        AND latitude <= ? AND latitude >= ? AND longitude <= ? AND longitude >= ?
        GROUP BY user""", t)

	usersArround = []
	for row in users.fetchall():
		usersArround.append(row[0])

	conn.close()
	return usersArround

	

def getUserDistancesTest():
	conn = sqlite3.connect('databases/locations.db')
	c = conn.cursor()

	resultPoints = c.execute("SELECT * FROM locations")

	point = resultPoints.fetchone()
	for row in resultPoints:
		dist = utils.locationDistance(point[2], point[3], row[2], row[3])
		print("Distance: " + str(dist))

	conn.close()

#getUserDistancesTest()
#map = getUserLocationMap("Javierd", 40.3591933, -3.6855106)
#print(map)
#postUserLocation("tvdh", 40.35141938, -3.68455186, 1504206094638)


#DEPRECATED
def getUserLocationMapDEPRECATED(name, latitude, longitude):
	userMap = []
	conn = sqlite3.connect('databases/locations.db')
	c = conn.cursor()

	timestamp = utils.timeInMillis()
	#Use just the last 30 minutes of data
	pastTS = timestamp - 300 * 60 * 1000
	#Get the points around aprox 1,1 km each side
	maxLat = latitude + 0.01
	minLat = latitude - 0.01
	maxLng = longitude + 0.01
	minLng = longitude - 0.01

	t = (name, pastTS, maxLat, minLat, maxLng, minLng)

	resultPoints = c.execute("""SELECT latitude, longitude,
        MAX(timestamp) AS timestamp
        FROM locations
        WHERE user != ? AND timestamp >= ?
        AND latitude <= ? AND latitude >= ? AND longitude <= ? AND longitude >= ?
        GROUP BY user""", t)

	for row in resultPoints:
		point = utils.setUpPlace(row[0], row[1], 10, 'name', 'desc', 'url')
		userMap.append(point)

	conn.close()
	return userMap
