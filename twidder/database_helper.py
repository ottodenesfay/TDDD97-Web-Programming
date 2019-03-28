import sqlite3
import random
import string
from passlib.hash import sha256_crypt
from flask import current_app, g
from flask.cli import with_appcontext


def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    with open('schema.sql') as f:
        c.executescript(f.read())


def checkEmailExist(email):## checks if email exists in Users, return value: bool
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT rowid FROM Users WHERE Email=?", (email,))
    data = c.fetchone()
    if data is None:
        return False
    else:
        return True

def IncrementPostCountForUser(email): ## increments users post counter (keeps track of # of posts the user made), return value: none
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE Users SET PostCount = Postcount + 1 WHERE Email = ?", (email,))
    conn.commit()


def checkPassword(email, password): ## verifys the password given by user with the password stored in database, return value: bool
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT Password FROM Users WHERE Email=?", (email,))
    data = c.fetchone()
    if (sha256_crypt.verify(password, data[0])): ## verifys the password with the hash stored in database
        return True
    else:
        return False

def getNickByEmail(email): ## fetches the users nickname, return value: string
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT Nick FROM Users WHERE Email=?", (email,))
    data = c.fetchone()
    return data[0]

def postMessageToEmail(token, content, toEmail):## posts message to a users table, return value: JSON object
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if (checkLoggedIn(token)):
        if (checkEmailExist(toEmail)):
            email = generateNickFromEmail(toEmail)
            fromEmail = TokenToEmail(token)
            statement = "INSERT INTO " + email + " (FromEmail, Content) VALUES (?,?)"
            c.execute(statement, (fromEmail, content))
            conn.commit()
            IncrementPostCountForUser(fromEmail)
            return {"success": True, "message": "Message posted"}
        else:
            return {"success": False, "message": "No such user."}
    else:
        return {"success": False, "message": "You are not signed in."}


def getMessagesByToken(token): ## returns a users messages by token, return value: list of strings
    email = TokenToEmail(token)
    return getMessagesByEmail(token, email)


def getMessagesByEmail(token, email): ## returns a users messages by email, return value: list of strings
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if (checkLoggedIn(token)):
        if (checkEmailExist(email)):
            fromEmail = generateNickFromEmail(email)
            statement = "SELECT FromEmail, Content FROM " + fromEmail + ""
            c.execute(statement)
            Messages = []
            rows = c.fetchall()
            for row in rows:
                userPic = getUsersPicByEmail(token, row[0]) + ".jpg"
                data = {"writer": row[0], "content": row[1], "profilepic": userPic}
                Messages.insert(0,data)
            return {"success": True, "message": "User messages retrieved.", "data": Messages}
        else:
            return {"success": False, "message": "No such user."}
    return {"success": False, "message": "You are not signed in."}


def generateNickFromEmail(email): ## generates a neckname for user, return value: string
    newstr = email.replace("@", "")
    nickname = newstr.replace(".", "")
    return nickname

def addNewUser(userObject): ## adds new user to Users database, return value: JSON object
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if not checkEmailExist(userObject['Email']):
        enc_password = sha256_crypt.encrypt(userObject['Password']) ## encrypt password using sha256
        userNick = generateNickFromEmail(userObject['Email']) ## generate nickname for user
        c.execute("INSERT INTO Users (Email, Nick, Password, Firstname, Familyname, Gender, City, Country) VALUES (?,?,?,?,?,?,?,?)", (userObject['Email'], userNick, enc_password, userObject['FirstName'],
                                                            userObject['FamilyName'], userObject['Gender'], userObject['City'], userObject['Country']))
        conn.commit()
        if (c.rowcount == 1):
            statement = "CREATE TABLE IF NOT EXISTS " + userNick + " ( `FromEmail` TEXT, `Content` TEXT)" ## create table for users messages
            c.execute(statement)
            conn.commit()
            return {"success": True, "message": "Successfully created a new user."};
        else:
            return {"success": False, "message": "Form data missing or incorrect type."};
    else:
        return {"success": False, "message": "User already exists."}

def generateToken(): ## generate a unique token, return value: string
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(36))

def addUserToActive(email, password): ## adds user to ActiveUsers table, return value: JSON object
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if checkEmailExist(email):
        if (checkPassword(email, password)):
            token = generateToken()
            c.execute('INSERT INTO ActiveUsers (Token, Email) VALUES (?,?)', (token, email,))
            conn.commit()
            return {"success": True, "message": "Successfully signed in.", "data": token}
        else:
            return {"success": False, "message": "Wrong password."}
    else:
        return {"success": False, "message": "The email does not exist."}


def delUserFromActive(token): ## removes user from ActiveUsers table, return value: JSON object
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if checkLoggedIn(token):
        c.execute('DELETE FROM ActiveUsers WHERE Token=?', (token,))
        conn.commit()
        return {"success": True, "message": "Successfully signed out."}
    else:
        return {"success": False, "message": "You are not signed in."}

def changePasswordForUser(token, oldPassword, newPassword): ## changes password for user, return value: JSON object
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if (checkLoggedIn(token)):
        email = TokenToEmail(token)
        c.execute("SELECT Password FROM Users WHERE Email=?", (email,))
        dbPassword = c.fetchone()
        if (sha256_crypt.verify(oldPassword, dbPassword[0])): ##verify old password with password stored in database
            encNewPassword = sha256_crypt.encrypt(newPassword) ##encrypt new password
            c.execute("UPDATE Users SET Password=? WHERE Email = ?", (encNewPassword, email,))
            conn.commit()
            return {"success": True, "message": "Password changed."}
        else:
            return {"success": False, "message": "Wrong password."}
    else:
        return {"success": False, "message": "You are not logged in."}

def tokenToNick(token): ## get nickname for a user by token, return value: string
    email = TokenToEmail(token)
    return getNickByEmail(email)

def checkLoggedIn(token):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT rowid FROM ActiveUsers WHERE Token=?", (token,))
    data = c.fetchone()
    if data is None:
        return False
    else:
        return True


def checkLoggedInWithEmail(email): ## check if user logged in by email, return value: bool
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT rowid FROM ActiveUsers WHERE Email=?", (email,))
    data = c.fetchone()
    if data is None:
        return False
    else:
        return True

def TokenToEmail(token): ## get email for user by token, return value: string
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT Email FROM ActiveUsers WHERE Token=?", (token,))
    data = c.fetchone()
    return data[0]


def emailToToken(email): ## get token for user by email, return value: string
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT Token FROM ActiveUsers WHERE Email=?", (email,))
    data = c.fetchone()
    return data[0]

def getUsersPicByToken(token): ## get filename for users pic by token, return value: string
    email = TokenToEmail(token)
    return getUsersPicByEmail(token, email)

def updateUsersPic(token): ## set Haspic to 1 for user (indicating it has a profile pic), return value: none
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if (checkLoggedIn(token)):
        email = TokenToEmail(token)
        c.execute("UPDATE Users SET HasPic=1 WHERE Email = ?", (email,))
        conn.commit()


def getUsersPicByEmail(token, email): ## get filename for users pic by email, return value: string
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if (checkLoggedIn(token)):
        c.execute("SELECT HasPic FROM Users WHERE email=?", (email,))
        data = c.fetchone()
        if (data[0] == 1): ##if user has custom pic
            return getNickByEmail(email)
        else: ## load default profile pic
            return "defprofile"


def getUserByEmail(token, email): ## get users profile data by email, return value: JSON object
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if (checkLoggedIn(token)):
        c.execute("SELECT Email, Firstname, Familyname, Gender, City, Country, Nick FROM Users WHERE Email=?", (email,))
        data = c.fetchone()
        if data is None:
            return {"success": False, "message": "No such user."}
        else:
            filepath = "static/profilepics/" + data[6] + ".jpg"
            dataObject = {
                "email": data[0],
                "firstname": data[1],
                "familyname": data[2],
                "gender": data[3],
                "city": data[4],
                "country": data[5],
                "imgpath": filepath
            }
            return {"success": True, "message": "User messages retrieved.", "data": dataObject}
    else:
        return {"success": False, "message": "You are not signed in."}

def getUserByToken(token): ## get users profile data by token, return value: JSON object
    email = TokenToEmail(token)
    return getUserByEmail(token, email)

def getStatsForUser(token): ## get post statistics for user (used for graph), return value: JSON object
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if (checkLoggedIn(token)):
        email = TokenToEmail(token)
        nick = getNickByEmail(email)
        c.execute("SELECT PostCount FROM Users WHERE email=?", (email,)) ## fetch amount of posts user has made
        data = c.fetchone()
        postCount = data[0]

        c.execute("SELECT FromEmail FROM " + nick + "") ## fetch users messages
        rows = c.fetchall()
        postsByMe = 0
        totalPosts = len(rows)
        for row in rows:
            if (row[0] == email): ## if post is made by user
                postsByMe = postsByMe + 1 ## count posts by user
        dataObject = {
            "totalPostsByMe": postCount,
            "postsByMeOnMyWall": postsByMe,
            "PostByOthersOnMyWall": totalPosts - postsByMe
        }
        return {"success": True, "message": "Successfully fethced statistics.", "data": dataObject}
    else:
        return {"success": False, "message": "You are not signed in."}
