import bcrypt
import hashlib
import utils

def userSignIn(conn, mail, password):
	#0 = OK, 1 = Wrong user name, 2 = wrong password
	c = conn.cursor()

	c.execute("SELECT password, token, id FROM users WHERE mail = ?", (mail.lower(),))
	dbPass = c.fetchone()
	if(dbPass == None):
		return utils.setUpUserInfo(1, "None", "None")

	if not bcrypt.checkpw(password.encode('utf8'), dbPass[0]):
		return utils.setUpUserInfo(2, "None", "None")

	return utils.setUpUserInfo(0, dbPass[2], dbPass[1])

def userSignUp(conn, name, password, mail, sex, birthdate, styles):
	#0 = OK, 1 = username in use, 2 = email in use, 3 = Wrong email, 4 = other error
	c = conn.cursor()

	#Check if user name or email are already used
	c.execute("SELECT * FROM users WHERE id = ?", (name.lower(),))
	if(len(c.fetchall()) != 0):
		return utils.setUpUserInfo(1, "None", "None")
	c.execute("SELECT id FROM users WHERE mail = ?", (mail.lower(),))
	if(len(c.fetchall()) != 0):
		return utils.setUpUserInfo(2, "None", "None")

	hashedPass = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
	token = hashlib.sha256((name+password).encode('utf8')).hexdigest()


	t = (name.lower(), hashedPass, mail.lower(), str(token), sex, birthdate, styles)
	c.execute("INSERT INTO users(id, password, mail, token, sex, birthdate, styles) VALUES (?, ?, ?, ?, ?, ?, ?)", t)
	conn.commit()
	return utils.setUpUserInfo(0, name.lower(), token.lower())

def authenticateUser(conn, name, token):
	#True = OK, False = Wrong user name/ token
	c = conn.cursor()

	c.execute("SELECT token FROM users WHERE id = ?", (name.lower(),))
	dbPass = c.fetchone()
	if(dbPass == None):
		return False

	if(token != dbPass[0]):
		return False

	return True

def userCheckMail(conn, mail):
	#0 = OK, 1 = Wrong user name, 2 = wrong password
	c = conn.cursor()

	#Check if email is already used
	c.execute("SELECT mail FROM users WHERE mail = ?", (mail.lower(),))
	dbPass = c.fetchone()
	if(dbPass == None):
		return 1

	return 0

def userCheckName(conn, name):
	#0 = OK, 1 = Wrong user name, 2 = wrong password
	c = conn.cursor()

	#Check if user name is already used
	c.execute("SELECT id FROM users WHERE id = ?", (name.lower(),))
	dbPass = c.fetchone()
	if(dbPass == None):
		#Free username
		return 0

	#Used username
	return 1

#DEPRECATED
def getUsersData(usersIds):
	usersData = []
	conn = sqlite3.connect('database.db')
	conn.execute("PRAGMA foreign_keys = 1")
	c = conn.cursor()

	for userId in usersIds:
		c.execute("SELECT sex, birthdate, styles FROM users where id = ?", (userId,))
		user = c.fetchone()
		if user == None:
			continue

		userData = [user[0], user[1], user[2]]
		usersData.append(userData)


	conn.close()
	return  usersData