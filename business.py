import time
import userDatabase as userDB
import locationsDatabase as locationsDB
import placesDatabase as placesDB
import utils

ageLabels = ['-18', '18-22', '23-28', '29-35', '36-40', '41-50', '51-60', '61-70', '+70']
sexLabels = ['Man', 'Woman', 'Other']
ageBgColors = ['rgba(255, 167, 38, 1)',
            	'rgba(239, 83, 80, 1)',
           		'rgba(171, 71, 188, 1)',
            	'rgba(255, 193, 7, 1)',
            	'rgba(92, 107, 192, 1)',
            	'rgba(66, 165, 245, 1)',
            	'rgba(38, 198, 218, 1)',
            	'rgba(102, 187, 106, 1)',
            	'rgba(212, 225, 87, 1)']

sexBgColors = [ 'rgba(66, 165, 245, 1)',
				'rgba(236, 64, 122, 1)',
                'rgba(171, 71, 188, 1)']

ageBorderColors = ['rgba(0, 0, 0, 0.7)',
                	'rgba(0, 0, 0, 0.7)',
                	'rgba(255, 206, 86, 0.7)',
                	'rgba(75, 192, 192, 0.7)',
                	'rgba(153, 102, 255, 0.7)',
                	'rgba(5, 192, 192, 0.7)',
                	'rgba(75, 192, 12, 0.7)',
                	'rgba(75, 1, 192, 0.7)',
                	'rgba(255, 159, 64, 0.7)']

sexBorderColors = ['rgba(0, 0, 0, 0.7)',
                	'rgba(0, 0, 0, 0.7)',
                	'rgba(255, 206, 86, 0.7)']


def businessSignIn(conn, mail, password):
	#0 = OK, 1 = Wrong user name, 2 = wrong password
	c = conn.cursor()

	c.execute("SELECT password, token, id FROM business WHERE mail = ?", (mail,))
	dbPass = c.fetchone()
	if(dbPass == None):
		1

	if not bcrypt.checkpw(password.encode('utf8'), dbPass[0]):
		2

	return 0

def businessSignUp(conn, place, password, mail):
	#0 = OK, 1 = username in use, 2 = email in use, 3 = Wrong email, 4 = other error
	c = conn.cursor()

	#Check if user name or email are already used
	c.execute("SELECT * FROM business WHERE id = ?", (name,))
	if(len(c.fetchall()) != 0):
		return 1
	c.execute("SELECT id FROM business WHERE mail = ?", (mail,))
	if(len(c.fetchall()) != 0):
		return 2

	hashedPass = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
	token = hashlib.sha256((name+password).encode('utf8')).hexdigest()


	t = (place, mail, hashedPass, str(token))
	c.execute("INSERT INTO business(placeId, mail, password, token) VALUES (?, ?, ?, ?)", t)
	conn.commit()
	return 0


#TODO change startTime and endTime wih the local opening and closing hours
def getBusinessUserData(conn, placeId, days):
	dateTS = utils.timeInMillis()
	usersInfo = []
	usersAge = [0, 0, 0, 0, 0, 0, 0, 0, 0]
	usersSex = [0, 0, 0]

	#TODO Allow multiple timestamps
	startTimestamp = dateTS - days*24*3600*1000

	location = placesDB.getPlaceLocation(conn, placeId)
	if(location == None):
		return "The place doesn't exists"

	#Get all the users that were arround that location since the timestamp (24h)
	#TODO Change the 100m number

	lat = location[0]
	lng = location[1]
	radius = 100
	#1.1m * radius
	maxLat = lat + 0.00001 * radius
	minLat = lat - 0.00001 * radius
	maxLng = lng + 0.00001 * radius
	minLng = lng - 0.00001 * radius
	t = (startTimestamp, dateTS, maxLat, minLat, maxLng, minLng)

	c = conn.cursor()
	c.execute("""SELECT sex, birthdate, styles FROM users 
					WHERE id IN (
						SELECT user
				        FROM locations
				        WHERE timestamp >= ? AND timestamp <= ?
				        AND latitude <= ? AND latitude >= ? AND longitude <= ? AND longitude >= ?
				        GROUP BY user)""", t)

	#From each user, get the age and sort from -18, 18-22, 23-28- 29-35- 36-40, 41-50, 51-60, 61-70, +70
	for user in c.fetchall():
		age = int ((dateTS - user[1])/(1000 * 3600 * 24 *365))

		#Sex
		if user[0] == 0:
			usersSex[0] +=1
		elif user[0] == 1:
			usersSex[1] +=1
		elif user[0] == 2:
			usersSex[2] +=1

		#Ages
		if age > 70:
			usersAge[8] += 1
		elif age > 60:
			usersAge[7] += 1
		elif age > 50:
			usersAge[6] += 1
		elif age > 40:
			usersAge[5] += 1
		elif age > 35:
			usersAge[4] += 1
		elif age > 29:
			usersAge[3] += 1
		elif age > 23:
			usersAge[2] += 1
		elif age > 18:
			usersAge[1] += 1
		else:
			usersAge[0] += 1

	usersInfo.append(usersSex)
	usersInfo.append(usersAge)

	return usersInfo


def getBusinessInflowData(conn, placeId, days):
	nowTimestamp = utils.dayInMillis()
	inflowDataValues = []
	inflowDataLabels = []

	location = placesDB.getPlaceLocation(conn, placeId)
	if(location == None):
		return "The place doesn't exists"

	#Get the number of users that were arround that location between the two timestamps
	#TODO Change the 100m number
	for i in reversed(range(0, days+1)):
		startTimestamp = nowTimestamp - (i+1)*24*3600*1000 
		endTimestamp = nowTimestamp - i*24*3600*1000 
		numUsers = locationsDB.getNumUsersArround(conn, location[0], location[1], 100, startTimestamp, endTimestamp)
		dateStr = utils.millisToDate(startTimestamp, "%d/%m/%Y")
		inflowDataValues.append(numUsers)
		inflowDataLabels.append(dateStr)

	return [inflowDataLabels, inflowDataValues]


#DEPRECATED
def getBusinessUserDataDEPRECATED(placeId, days):
	dateTS = utils.timeInMillis()
	usersInfo = []
	usersAge = [0, 0, 0, 0, 0, 0, 0, 0, 0]
	usersSex = [0, 0, 0]

	#TODO Allow multiple timestamps
	startTimestamp = dateTS - days*24*3600*1000

	location = placesDB.getPlaceLocation(placeId)
	if(location == None):
		return "The place doesn't exists"

	#Get all the users that were arround that location since the timestamp (24h)
	#TODO Change the 100m number
	usersArroundIds = locationsDB.getUsersArround(location[0], location[1], 100, startTimestamp, dateTS)

	usersData = userDB.getUsersData(usersArroundIds)
	#From each user, get the age and sort from -18, 18-22, 23-28- 29-35- 36-40, 41-50, 51-60, 61-70, +70
	for user in usersData:
		age = int ((dateTS - user[1])/(1000 * 3600 * 24 *365))

		#Sex
		if user[0] == 0:
			usersSex[0] +=1
		elif user[0] == 1:
			usersSex[1] +=1
		elif user[0] == 2:
			usersSex[2] +=1

		#Ages
		if age > 70:
			usersAge[8] += 1
		elif age > 60:
			usersAge[7] += 1
		elif age > 50:
			usersAge[6] += 1
		elif age > 40:
			usersAge[5] += 1
		elif age > 35:
			usersAge[4] += 1
		elif age > 29:
			usersAge[3] += 1
		elif age > 23:
			usersAge[2] += 1
		elif age > 18:
			usersAge[1] += 1
		else:
			usersAge[0] += 1

	usersInfo.append(usersSex)
	usersInfo.append(usersAge)

	return usersInfo