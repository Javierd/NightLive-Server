import userDatabase as userDB
import locationsDatabase as locationsDB
import placesDatabase as placesDB
import utils

pieLabels = ['-18', '18-22', '23-28', '29-35', '36-40', '41-50', '51-60', '61-70', '+70']
sexLabels = ['Man', 'Woman', 'Other']
pieLegend = 'User classified by age'
ageBgColors = ['rgba(255, 167, 38, 1)',
            	'rgba(239, 83, 80, 1)',
           		'rgba(171, 71, 188, 1)',
            	'rgba(255, 193, 7, 1)',
            	'rgba(92, 107, 192, 1)',
            	'rgba(66, 165, 245, 1)',
            	'rgba(38, 198, 218, 1)',
            	'rgba(102, 187, 106, 1)',
            	'rgba(212, 225, 87, 1)']

ageBorderColors = ['rgba(0, 0, 0, 0.7)',
                	'rgba(0, 0, 0, 0.7)',
                	'rgba(255, 206, 86, 0.7)',
                	'rgba(75, 192, 192, 0.7)',
                	'rgba(153, 102, 255, 0.7)',
                	'rgba(5, 192, 192, 0.7)',
                	'rgba(75, 192, 12, 0.7)',
                	'rgba(75, 1, 192, 0.7)',
                	'rgba(255, 159, 64, 0.7)']

sexBgColors = [ 'rgba(66, 165, 245, 1)',
				'rgba(236, 64, 122, 1)',
                'rgba(171, 71, 188, 1)']

def getBusinessAgeData(placeId, days):
	numUsers = 0
	dateTS = utils.timeInMillis()
	usersInfo = []
	usersAge = [0, 0, 0, 0, 0, 0, 0, 0, 0]
	usersSex = [0, 0, 0]

	#TODO Allow multiple timestamps
	timestamp = dateTS - days*24*3600*1000

	location = placesDB.getPlaceLocation(placeId)
	if(location == None):
		return "The place doesn't exists"

	#Get all the users that were arround that location since the timestamp (24h)
	#TODO Change the 100m number
	usersArroundIds = locationsDB.getUsersArround(location[0], location[1], 100, timestamp)

	usersData = userDB.getUsersData(usersArroundIds)
	#From each user, get the age and sort from -18, 18-22, 23-28- 29-35- 36-40, 41-50, 51-60, 61-70, +70
	for user in usersData:
		numUsers += 1
		age = int ((dateTS - user[1])/(1000 * 3600 * 24 *365))

		#Sex
		if user[0] == '0':
			usersSex[0] +=1
		elif user[0] == '1':
			usersSex[1] +=1
		elif user[0] == '2':
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