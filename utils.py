import time
import math
import sqlite3
import bcrypt
from random import randint
from datetime import datetime, timezone, date
from PIL import Image

users_table_sql = """CREATE TABLE IF NOT EXISTS users(
							id TEXT PRIMARY KEY,
							mail TEXT UNIQUE NOT NULL,
							password TEXT NOT NULL,
							sex INTEGER NOT NULL,
							birthdate BLOB NOT NULL,
							styles TEXT,
							friends TEXT
						);"""

locations_table_sql = """CREATE TABLE IF NOT EXISTS locations(
							id INTEGER PRIMARY KEY AUTOINCREMENT,
							user TEXT NOT NULL,
							latitude REAL NOT NULL,
							longitude REAL NOT NULL,
							timestamp BLOB NOT NULL,
							public INTEGER,
							FOREIGN KEY (user) REFERENCES users(id)
						);"""

places_table_sql = """CREATE TABLE IF NOT EXISTS places(
							id TEXT PRIMARY KEY,
							latitude REAL NOT NULL,
							longitude REAL NOT NULL,
							style TEXT,
							startTimestamp BLOB NOT NULL,
							endTimestamp BLOB NOT NULL
						);"""

business_table_sql = """CREATE TABLE IF NOT EXISTS business(
							id INTEGER PRIMARY KEY AUTOINCREMENT,
							placeId TEXT NOT NULL,
							mail TEXT UNIQUE NOT NULL,
							password TEXT NOT NULL,
							token TEXT,
							FOREIGN KEY (placeId) REFERENCES places(id)
						);"""

flyers_table_sql = """CREATE TABLE IF NOT EXISTS flyers(
							id INTEGER PRIMARY KEY AUTOINCREMENT,
							name TEXT,
							placeId TEXT NOT NULL,
							price REAL NOT NULL,
							image TEXT,
							qr TEXT,
							info TEXT,
							startTimestamp BLOB,
							endTimestamp BLOB,
							FOREIGN KEY (placeId) REFERENCES places(id)
						);"""


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

def dayInMillis():
	#Return the time in millis at a fixed hour
	#12:00 AM
	#TODO Check if UTC time could cause any trouble with the hours and dates
	dt = datetime.now(timezone.utc)
	dt = dt.replace(hour=12, minute=0, second=0, microsecond=0)
	return int(round(dt.timestamp()*1000))

def millisToDate(millis, format):
	d = date.fromtimestamp(millis/1000)
	return d.strftime(format)

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

def setUpUserInfo(result, name, token):
	user = {
		'result' : result,
		'name' : name,
		'token' : token
	}
	return user

def setUpFlyer(price, image, qr, info, startTimestamp, endTimestamp):
	flyer = {
		'price' : price,
		'image' : image,
		'qr' : qr,
		'info' : info,
		'startTimestamp' : startTimestamp,
		'endTimestamp' : endTimestamp
	}
	return flyer

def imageHexColor(filename):
	i = Image.open(filename)
	h = i.histogram()

	# split into red, green, blue
	r = h[0:256]
	g = h[256:256*2]
	b = h[256*2: 256*3]

	# perform the weighted average of each channel:
	# the *index* is the channel value, and the *value* is its weight
	red = sum(r)
	green = sum(g)
	blue = sum(b)
	if(red > 0):
		red = sum( i*w for i, w in enumerate(r) ) / red
	else:
		red = 0

	if(green > 0):
		green = sum( i*w for i, w in enumerate(g) ) / green
	else:
		green = 0

	if(blue > 0):
		blue = sum( i*w for i, w in enumerate(b) ) / blue
	else:
		blue = 0

	return '#'+format(red, 'X').zfill(2)+format(green, 'X').zfill(2)+format(blue, 'X').zfill(2)
	

def locationDistance(lat1, long1, lat2, long2):
	#delta 0.0001 = 11m
	deltaLat = lat2 - lat1
	deltaLong = long2 - long1

	deltaLat = 11 * (deltaLat / 0.0001)
	deltaLong = 11 * (deltaLong / 0.0001)

	distance = math.sqrt(math.pow(deltaLat, 2) + math.pow(deltaLong, 2))
	return distance
	
def generateRandomPoints():
	conn = sqlite3.connect('database.db')
	conn.execute("PRAGMA foreign_keys = 1")
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

			t = ('user'+str(k*20 +i), lat, lon, timestamp, 1)
			c.execute("INSERT INTO locations(user, latitude, longitude, timestamp, public) VALUES (?, ?, ?, ?, ?)", t)
			conn.commit()
			j += 1
		k += 1

	conn.close()

def generateUsers():
	conn = sqlite3.connect('database.db')
	conn.execute("PRAGMA foreign_keys = 1")
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
		token = "123456789ABCDEF"
		t = (name, password, mail, sex, birthdate, token)
		c.execute("INSERT INTO users(id, password, mail, sex, birthdate, token) VALUES (?, ?, ?, ?, ?, ?)", t)
	
	conn.commit()
	conn.close()

def createDatabase():
	conn = sqlite3.connect('database.db')
	c = conn.cursor()
	c.execute(users_table_sql)
	c.execute(locations_table_sql)
	c.execute(places_table_sql)
	c.execute(business_table_sql)
	c.execute(flyers_table_sql)
	conn.commit()
	conn.close()

#createDatabase()
generateRandomPoints()
#generateUsers()