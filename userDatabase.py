import sqlite3


def userSignIn(mail, password):
	#0 = OK, 1 = Wrong user name, 2 = wrong password
	conn = sqlite3.connect('databases/users.db')
	c = conn.cursor()

	c.execute("SELECT password, name FROM users WHERE mail = ?", (mail,))
	dbPass = c.fetchone()
	if(dbPass == None):
		conn.close()
		return 1

	if(dbPass[0] != password):
		conn.close()
		return 2

	conn.close()
	return dbPass[1]

def userSignUp(name, password, mail, sex, birthdate, styles):
	#0 = OK, 1 = username in use, 2 = email in use, 3 = Wrong email, 4 = other error
	conn = sqlite3.connect('databases/users.db')
	c = conn.cursor()

	#Check if user name or email are already used
	c.execute("SELECT id FROM users WHERE name = ?", (name,))
	if(len(c.fetchall()) != 0):
		return 1
	c.execute("SELECT id FROM users WHERE mail = ?", (mail,))
	if(len(c.fetchall()) != 0):
		return 2

	t = (name, password, mail, sex, birthdate, styles)
	c.execute("INSERT INTO users(name, password, mail, sex, birthdate, styles) VALUES (?, ?, ?, ?, ?, ?)", t)
	conn.commit()
	conn.close()
	return 0

def userCheckMail(mail):
	#0 = OK, 1 = Wrong user name, 2 = wrong password
	conn = sqlite3.connect('databases/users.db')
	c = conn.cursor()

	#Check if email is already used
	c.execute("SELECT mail FROM users WHERE mail = ?", (mail,))
	dbPass = c.fetchone()
	if(dbPass == None):
		conn.close()
		return 1

	conn.close()
	return 0

def userCheckName(name):
	#0 = OK, 1 = Wrong user name, 2 = wrong password
	conn = sqlite3.connect('databases/users.db')
	c = conn.cursor()

	#Check if user name is already used
	c.execute("SELECT name FROM users WHERE name = ?", (name,))
	dbPass = c.fetchone()
	if(dbPass == None):
		conn.close()
		#Free username
		return 0

	conn.close()
	#Used username
	return 1

def getUsersData(usersIds):
	usersData = []
	conn = sqlite3.connect('databases/users.db')
	c = conn.cursor()

	for userId in usersIds:
		c.execute("SELECT sex, birthdate, styles FROM users where name = ?", (userId,))
		user = c.fetchone()
		if user == None:
			continue

		userData = [user[0], user[1], user[2]]
		usersData.append(userData)


	conn.close()
	return  usersData
