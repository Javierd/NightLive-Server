import utils
import userDatabase as userDB
import locationsDatabase as locationsDB
import business
import sqlite3
from flask import Flask, request, jsonify, render_template, _app_ctx_stack

server = Flask(__name__)
DATABASE = 'database.db'

def get_db():
	db = getattr(_app_ctx_stack.top , '_database', None)
	if db is None:
		conn = sqlite3.connect(DATABASE)
		conn.execute("PRAGMA foreign_keys = 1")
		db = _app_ctx_stack.top._database = conn
	return db

@server.teardown_appcontext
def close_connection(exception):
	db = getattr(_app_ctx_stack.top, '_database', None)
	if db is not None:
		db.commit()
		db.close()

@server.route('/')
def index():
	return 'Hello world'

@server.route('/location', methods=['GET', 'POST'])
def location():
	if request.method == 'POST':

		if 'lat' in request.args and 'long' in request.args and 'user' in request.args and 'public' in request.args and 'token' in request.args:

			latitude = float(request.args.get('lat'))
			longitude = float(request.args.get('long'))
			user = request.args.get('user')
			token = request.args.get('token')
			public = int(request.args.get('public'))

			
			result = locationsDB.postUserLocation(get_db(), user, token, latitude, longitude, public)
			if(result == 1):
				return "1", 401 #Unauthorized

			return '"'+str(result)+'"'
		else:
			return "-1", 400
	else:

		if 'lat' in request.args and 'long' in request.args and 'user' in request.args and 'token' in request.args:

			latitude = float(request.args.get('lat'))
			longitude = float(request.args.get('long'))
			user = request.args.get('user')
			token = request.args.get('token')

			userMap = locationsDB.getUserLocationMap(get_db(), user, token, latitude, longitude)
			
			if(userMap == 1):
				return "1", 401 #Unauthorized
			return jsonify({'points': userMap})
		else:
			return 'La direccion no esta correctamente formada', 400

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
			result = userDB.userSignUp(get_db(), name, password, mail, sex, birthdate, styles)
			return jsonify({'user': result})
		else:
			return jsonify({'user': utils.setUpUserInfo(-1, "None", "None")}), 400
	else:

		if 'mail' in request.args and 'pass' in request.args:

			mail = request.args.get('mail')
			password = request.args.get('pass')

			result = userDB.userSignIn(get_db(), mail, password)
			return jsonify({'user': result})
		else:
			return jsonify({'user': utils.setUpUserInfo(-1, "None", "None")}), 400

@server.route('/business', methods=['GET'])
def businessData():
	if 'placeId' in request.args:

		placeId = request.args.get('placeId')
		#Sorted from man, woman, other, -18, 18-22, 23-28- 29-35- 36-40, 41-50, 51-60, 61-70, +70
		#TODO Allow multiple timestamps
		userInfo = business.getBusinessUserData(get_db(), placeId, 1)
		inflowData = business.getBusinessInflowData(get_db(), placeId, 15)
		#userAges = [12, 16, 2, 3, 12, 18, 27, 15, 11, 7, 4, 1]

		return render_template('user_age_chart.html', 
			usersValues=userInfo, 
			usersLabels=[business.sexLabels, business.ageLabels],
			usersBgColors=[business.sexBgColors, business.ageBgColors], 
			usersBorderColors=[business.sexBorderColors, business.ageBorderColors],
			inflowValues=inflowData[1],
			inflowLabels=inflowData[0])
	else:
		return "-1", 400

@server.route('/user/check', methods=['GET'])
def userCheck():
	if 'mail' in request.args:
		mail = request.args.get('mail')

		result = userDB.userCheckMail(get_db(), mail)
		return '"'+str(result)+'"'
	elif 'name' in request.args:
		name = request.args.get('name')

		result = userDB.userCheckName(get_db(), name)
		return '"'+str(result)+'"'
	else:
		return "-1", 400

if __name__ == '__main__':
	server.run(debug=True, host='0.0.0.0', port=5000)