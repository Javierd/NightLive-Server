import sqlite3
import time
import numpy as np
from threading import Thread
import utils
import dbscan
import placesDatabase as placesDB
import userDatabase as userDB

#Distance in meters
minDist = 20
minPoints = 10

#public in database: 0=hidden 1=public for friends, 2=everybody
def storePlacesIdArroundUser(latitude, longitude):
	conn = sqlite3.connect('database.db')
	conn.execute("PRAGMA foreign_keys = 1")
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

	if(c.fetchone == None):
		#Update / get the places in a separate thread
		conn.close()
		thread = Thread(target = placesDB.getPlacesAtPointFromGMaps, args = (latitude, longitude))
		thread.start()	
	else:
		conn.close()

def postUserLocation(name, token, latitude, longitude, public):
	#0 = OK, 1 = Wrong user
	conn = sqlite3.connect('database.db')
	conn.execute("PRAGMA foreign_keys = 1")
	c = conn.cursor()

	if(userDB.authenticateUser(name, token) == False):
		return 1

	#Store the location
	timestamp = utils.timeInMillis()

	t = (name, latitude, longitude, timestamp, public)
	c.execute("INSERT INTO locations(user, latitude, longitude, timestamp, public) VALUES (?, ?, ?, ?, ?)", t)
	conn.commit()
	conn.close()

	storePlacesIdArroundUser(latitude, longitude)

	return 0

def getUserLocationMap(name, token, latitude, longitude):
	#1=Wrong user
	userMap = []
	conn = sqlite3.connect('database.db')
	conn.execute("PRAGMA foreign_keys = 1")
	c = conn.cursor()

	if(userDB.authenticateUser(name, token) == False):
		return 1

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
		#print(clusterPoint)
		#Get the places arround
		radius = utils.getRadius(clusterPoint[2])

		#TODO Change the radius
		deltaRad = 0.0004 * radius #0.00001 = 1.1m
		maxLat = clusterPoint[0] + deltaRad
		minLat = clusterPoint[0] - deltaRad
		maxLng = clusterPoint[1] + deltaRad
		minLng = clusterPoint[1] - deltaRad

		t = (maxLat, minLat, maxLng, minLng)
		placesArround = c.execute("SELECT id, latitude, longitude FROM places WHERE latitude <= ? AND latitude >= ? AND longitude <= ? AND longitude >= ?", t)
		places = []
		for row in placesArround:
			#print("\t"+str(row))
			place = utils.setUpGMapPlace(row[0], row[1], row[2])
			places.append(place)

		if len(places) > 0 : 
			point = utils.setUpPoint(clusterPoint[0], clusterPoint[1], radius, places)
			userMap.append(point)

	conn.close()
	return userMap

#DEPRECATED
def getUsersArround(lat, lng, radius, startTimestamp, endTimestamp):
	conn = sqlite3.connect('database.db')
	conn.execute("PRAGMA foreign_keys = 1")
	c = conn.cursor()


	#1.1m * radius
	maxLat = lat + 0.00001 * radius
	minLat = lat - 0.00001 * radius
	maxLng = lng + 0.00001 * radius
	minLng = lng - 0.00001 * radius
	t = (startTimestamp, endTimestamp, maxLat, minLat, maxLng, minLng)

	users = c.execute("""SELECT user
        FROM locations
        WHERE timestamp >= ? AND timestamp <= ?
        AND latitude <= ? AND latitude >= ? AND longitude <= ? AND longitude >= ?
        GROUP BY user""", t)

	usersArround = []
	for row in users.fetchall():
		usersArround.append(row[0])

	conn.close()
	return usersArround

def getNumUsersArround(lat, lng, radius, startTimestamp, endTimestamp):
	conn = sqlite3.connect('database.db')
	conn.execute("PRAGMA foreign_keys = 1")
	c = conn.cursor()

	#1.1m * radius
	maxLat = lat + 0.00001 * radius
	minLat = lat - 0.00001 * radius
	maxLng = lng + 0.00001 * radius
	minLng = lng - 0.00001 * radius
	t = (startTimestamp, endTimestamp, maxLat, minLat, maxLng, minLng)

	users = c.execute("""SELECT user
        FROM locations
        WHERE timestamp >= ? AND timestamp <= ?
        AND latitude <= ? AND latitude >= ? AND longitude <= ? AND longitude >= ?
        GROUP BY user""", t)

	numUsers = 0
	for row in users.fetchall():
		numUsers += 1

	conn.close()
	return numUsers


	

def getUserDistancesTest():
	conn = sqlite3.connect('databases.db')
	conn.execute("PRAGMA foreign_keys = 1")
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
