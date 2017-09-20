import utils
import userDatabase as userDB
import locationsDatabase as locationsDB
import business
from flask import Flask, request, jsonify, render_template

server = Flask(__name__)

@server.route('/')
def index():
	return 'Hello world'

@server.route('/location', methods=['GET', 'POST'])
def location():
	if request.method == 'POST':

		if 'lat' in request.args and 'long' in request.args and 'user' in request.args and 'public' in request.args:

			latitude = float(request.args.get('lat'))
			longitude = float(request.args.get('long'))
			user = request.args.get('user')
			public = int(request.args.get('public'))

			result = locationsDB.postUserLocation(user, latitude, longitude, public)
			return '"'+str(result)+'"'
		else:
			return "-1"
	else:

		if 'lat' in request.args and 'long' in request.args and 'user' in request.args:

			latitude = float(request.args.get('lat'))
			longitude = float(request.args.get('long'))
			user = request.args.get('user')

			userMap = locationsDB.getUserLocationMap(user, latitude, longitude)
			return jsonify({'points': userMap})
		else:
			return 'La direccion no esta correctamente formada'

@server.route('/user', methods=['GET', 'POST'])
def user():
	if request.method == 'POST':

		if 'name' in request.args and 'pass' in request.args and 'sex' in request.args and 'mail' in request.args and 'birthdate' in request.args and 'styles' in request.args:

			name = str(request.args.get('name'))
			password = str(request.args.get('pass'))
			sex = request.args.get('sex')
			mail = request.args.get('mail')
			birthdate = int(request.args.get('birthdate'))
			styles = request.args.get('styles')

			#TODO comprobar el email y mandar un error si no existe
			result = userDB.userSignUp(name, password, mail, sex, birthdate, styles)
			return '"'+str(result)+'"'
		else:
			return "-1"
	else:

		if 'mail' in request.args and 'pass' in request.args:

			mail = request.args.get('mail')
			password = request.args.get('pass')

			result = userDB.userSignIn(mail, password)
			return '"'+str(result)+'"'
		else:
			return "-1"

@server.route('/business', methods=['GET'])
def businessData():
	if 'placeId' in request.args:

		placeId = request.args.get('placeId')
		#Sorted from man, woman, other, -18, 18-22, 23-28- 29-35- 36-40, 41-50, 51-60, 61-70, +70
		#TODO Allow multiple timestamps
		userInfo = business.getBusinessAgeData(placeId, 1)
		inflowData = business.getBusinessInflowData(placeId, 15)
		#userAges = [12, 16, 2, 3, 12, 18, 27, 15, 11, 7, 4, 1]

		return render_template('user_age_chart.html', 
			usersValues=userInfo, 
			usersLabels=[business.sexLabels, business.ageLabels],
			usersBgColors=[business.sexBgColors, business.ageBgColors], 
			usersBorderColors=[business.sexBorderColors, business.ageBorderColors],
			inflowValues=inflowData[1],
			inflowLabels=inflowData[0])
	else:
		return "-1"

@server.route('/user/check', methods=['GET'])
def userCheck():
	if 'mail' in request.args:
		mail = request.args.get('mail')

		result = userDB.userCheckMail(mail)
		return '"'+str(result)+'"'
	elif 'name' in request.args:
		name = request.args.get('name')

		result = userDB.userCheckName(name)
		return '"'+str(result)+'"'
	else:
		return "-1"



if __name__ == '__main__':
	server.run(debug=True, host='0.0.0.0', port=5000)