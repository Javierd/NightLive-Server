from flask import Flask, request, jsonify, render_template, redirect, url_for, _app_ctx_stack, send_from_directory, flash
import os
import utils
import userDatabase as userDB
import locationsDatabase as locationsDB
import business
import sqlite3
from websiteServer import web_page

DATABASE = 'database.db'
FLYER_IMAGE_UPLOAD_FOLDER = './FlyerImages'
FLYER_IMAGE_ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


server = Flask(__name__)
server.register_blueprint(web_page)
server.config['FLYER_IMAGE_UPLOAD_FOLDER'] = FLYER_IMAGE_UPLOAD_FOLDER
server.secret_key = '\x07\xcd\xc8\x84\xd8s9tO{\xbc\x1e\xac^|>\xf5\xce\xe8\xb8\xe2\xa5\x01H'
#Limit the images size to 16 MBytes
server.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def get_db():
	db = getattr(_app_ctx_stack.top , '_database', None)
	if db is None:
		conn = sqlite3.connect(DATABASE)
		conn.execute("PRAGMA foreign_keys = 1")
		db = _app_ctx_stack.top._database = conn
	return db

def flyer_allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in FLYER_IMAGE_ALLOWED_EXTENSIONS

@server.teardown_appcontext
def close_connection(exception):
	db = getattr(_app_ctx_stack.top, '_database', None)
	if db is not None:
		db.commit()
		db.close()

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

		return render_template('business_data.html', 
			usersValues=userInfo, 
			usersLabels=[business.sexLabels, business.ageLabels],
			usersBgColors=[business.sexBgColors, business.ageBgColors], 
			usersBorderColors=[business.sexBorderColors, business.ageBorderColors],
			inflowValues=inflowData[1],
			inflowLabels=inflowData[0])
	else:
		return "-1", 400

#TODO, ver como enviar el token y el placeid para que sea seguro, y activar este
@server.route('/business/flyers2', methods=['GET', 'POST'])
def flyers2():
	if request.method == 'POST':
		if 'name' in request.args and 'placeId' in request.args and 'token' in request.args and 'price' in request.args and 'imageUrl' in request.args and 'qrUrl' in request.args and 'info' in request.args and 'startTimestamp' in request.args and 'endTimestamp' in request.args:

			name = request.args.get('name')
			placeId = request.args.get('placeId')
			token = request.args.get('token')
			price = request.args.get('price')
			imageUrl = request.args.get('imageUrl')
			qrUrl = request.args.get('qrUrl')
			info = request.args.get('info')
			startTimestamp = request.args.get('startTimestamp')
			endTimestamp = request.args.get('endTimestamp')

			result = business.businessPostFlyer(get_db(), name, placeId, token, price, imageUrl, qrUrl, info, startTimestamp, endTimestamp)
			if(result == 1):
				return "1", 401 #Unauthorized

			return '"'+str(result)+'"'
		else:
			#TODO Flash de que falta algo
			return "-1", 400

	else:
		if 'placeId' in request.args:

			placeId = request.args.get('placeId')
			result = business.businessGetUsersFlyers(get_db(), placeId)
			return jsonify({'flyers': result})
		else:
			return "-1", 400

@server.route('/business/flyers', methods=['GET', 'POST'])
def flyers():
	if request.method == 'POST':
		imageUrl = None

		if 'image_uploads' in request.files:
			file = request.files['image_uploads']
			if file.filename != '' and file and flyer_allowed_file(file.filename):
				filename = utils.setFyerImageFileName("place", file.filename)
				file.save(os.path.join(server.config['FLYER_IMAGE_UPLOAD_FOLDER'], filename))
				#The [1:] allow us to remove the / of the start
				imageUrl = request.url_root+url_for('uploaded_file',filename=filename)[1:]


		if 'flyer_name' in request.form and 'flyer_price' in request.form and 'flyer_info' in request.form and 'start_date' in request.form and 'end_date' in request.form:

			name = request.form.get('flyer_name')
			price = request.form.get('flyer_price')

			info = request.form.get('flyer_info')
			#TODO pass those dates to milliseconds
			startTimestamp = utils.dateToMillis(request.form.get('start_date'), '%m/%d/%Y')
			endTimestamp = utils.dateToMillis(request.form.get('end_date'), '%m/%d/%Y')

			qrCode = None
			if 'flyer_qrCode' in request.form:
				qrCode = request.form.get('flyer_qrCode')

			result = business.businessPostFlyer(get_db(), name, "ChIJ2-1d6OsmQg0RbynEoIYgmw8", None, price, imageUrl, qrCode, info, startTimestamp, endTimestamp)
			if(result == 1):
				return "1", 401 #Unauthorized

			return '"'+str(result)+'"'
		else:
			#TODO Flash de que falta algo
			return "-1", 400

	else:
		if 'placeId' in request.args:

			placeId = request.args.get('placeId')
			result = business.businessGetUsersFlyers(get_db(), placeId)
			return jsonify({'flyers': result})
		else:
			return "-1", 400


@server.route('/flyers/images/<filename>')
def flyer_image(filename):
    return send_from_directory(server.config['FLYER_IMAGE_UPLOAD_FOLDER'],
                               filename)


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