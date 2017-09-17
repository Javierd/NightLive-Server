import time
import math
import sqlite3
from random import randint

people = [  [40.359105, -3.685292], #Casa
			[40.360143, -3.685635], #Calle generosidad
			[40.358580, -3.684649], #El espinillo
			[40.358768, -3.685797], #Mitad del edificio
			[40.358923, -3.685389], #Calle unanimidad 60 (al lado)
			[40.359275, -3.687824], #Rotonda avda felicidad
			[40.356315, -3.686311], #Residencia alzheimer
			[40.357177, -3.691644], #Felix Rubio
			[40.351234, -3.692000], #MediaMark
			[40.406587, -3.711562], #Puerta de toledo
			[40.420066, -3.705763]] #Callao

def timeInMillis():
	return int(round(time.time() * 1000))

def getRadius(numPoints):
	#Linear ecuation, f(15)=5, f(100)=60
	if(numPoints < 10):
		return 2
	return (int)(55/85 * numPoints + 5 - 55*15/85)


def setUpPoint(latitude, longitude, radius, places):
	point = {
		'latitude' : latitude,
		'longitude' : longitude,
		'radius' : radius,
		'places': places
	}
	return point

def setUpGMapPlace(id, latitude, longitude):
	place = {
		'id' : id,
		'latitude' : latitude,
		'longitude' : longitude
	}
	return place

def locationDistance(lat1, long1, lat2, long2):
	#delta 0.0001 = 11m
	deltaLat = lat2 - lat1
	deltaLong = long2 - long1

	deltaLat = 11 * (deltaLat / 0.0001)
	deltaLong = 11 * (deltaLong / 0.0001)

	distance = math.sqrt(math.pow(deltaLat, 2) + math.pow(deltaLong, 2))
	return distance
	
def generateRandomPoints():
	conn = sqlite3.connect('databases/locations.db')
	c = conn.cursor()

	j = 0
	k = 0
	for place in people:
		numPoints = randint(12, 20)
		for i in range(0, numPoints):
			timestamp = timeInMillis()
			#Max variation of aprox 10m
			sumLat = randint(-100, 100)/1000000
			sumLong = randint(-100, 100)/1000000
			lat = place[0]+sumLat
			lon = place[1]+sumLong

			t = ('user'+str(k*20 +i), lat, lon, timestamp, "country1", "city1", 1)
			c.execute("INSERT INTO locations(user, latitude, longitude, timestamp, country, city, public) VALUES (?, ?, ?, ?, ?, ?, ?)", t)
			conn.commit()
			j += 1
		k += 1

	conn.close()

def generateUsers():
	conn = sqlite3.connect('databases/users.db')
	c = conn.cursor()

	for i in range(0, 300):
		name = 'user'+str(i)
		mail = name+'@mail.com'
		password = name+'hello123'
		sex = 0
		if(i%2 == 0):
			sex = 1
		ageInYears = randint(16, 75)
		birthdate = timeInMillis() - ageInYears*365*24*3600*1000

		t = (name, password, mail, sex, birthdate)
		c.execute("INSERT INTO users(name, password, mail, sex, birthdate) VALUES (?, ?, ?, ?, ?)", t)
	
	conn.commit()
	conn.close()

#generateRandomPoints()
#generateUsers()