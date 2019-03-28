from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from geventwebsocket import WebSocketServer, WebSocketError
from geventwebsocket.handler import WebSocketHandler
import json ## for parsing etc
import os ##for saving files on cp
import database_helper as db ## file with database-based functions
import base64 ##for hashing
import hashlib ##for hashing
import hmac ##for hashing

app = Flask("twidder")

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

webSockets = {} ## dict of active websocket connections


##db = database_helper.Database()

def init_twidder():
    db.init_db() ##initiates database with schema.sql script
    print("Initiation done!")

@app.route('/SocketSetup')
def SocketSetup():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        data = json.loads(ws.receive())
        token =  data['token']
        webSockets[token] = ws
        dataObject = {"success": True,
                      "message": "Websocket online!"
                     }
        ws.send(json.dumps(dataObject))
        while True:
            data = ws.receive() ## to keep open the connection
            if data is None:
                del webSockets[token]
                ws.close()
                return ""
    return ""


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('client.html') ## render the html content


@app.route('/sign_in', methods=['POST'])
def sign_in():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if db.checkLoggedInWithEmail(email): ##if email already signed in
            tokenToDelete = db.emailToToken(email) ## get token for user to log out
            db.delUserFromActive(tokenToDelete) ## log out user
            ws = webSockets[tokenToDelete]
            dataObject = {"success": False,
                          "message": "You have been logged out!"
                          }
            ws.send(json.dumps(dataObject)) ## send log out message to user
            ws.close()

        status = db.addUserToActive(email, password) ## add new user to active
        return json.dumps(status)
    else:
        return ""

@app.route('/setProfilePic', methods=['POST'])
def setProfilePic():
    if request.method == 'POST':
        file = request.files['file']
        email = request.form['email']
        blob = request.form['blob']
        encMessage = request.form['hash']
        auth = verifyUser(email, encMessage, blob) ##verify users private key with database
        if (auth['success']):
            target = os.path.join(APP_ROOT, 'static/profilepics/') ##get path
            db.updateUsersPic(auth['token'])
            newFileName = db.tokenToNick(auth['token']) + ".jpg"
            file.filename = newFileName
            destination = "".join([target, newFileName])
            file.save(destination) ##save file to /profilepics folder
            filepath = "static/profilepics/" + newFileName
            return json.dumps({'success': True,
                               'message': 'Profile picture changed.',
                               'data': filepath})
        else:
            return json.dumps({'success': False,
                               'message': 'Could not verify user'
                               })
    else:
        return ""

@app.route('/getHomeProfilePic', methods=['POST'])
def getHomeProfilePic():
    if request.method == 'POST':
        email = request.form['email']
        userEmail = request.form['userEmail'] ##email of user to fetch pic
        blob = request.form['blob']
        encMessage = request.form['hash']
        auth = verifyUser(email, encMessage, blob)
        if (auth['success']):
            filename = db.getUsersPicByEmail(auth['token'], userEmail) + ".jpg" ##get filename of users profile pic
            filepath = "static/profilepics/" + filename
            return json.dumps({'success': True,
                               'data': filepath}) ##return filepath to client side
        else:
            return json.dumps({'success': False,
                               'message': 'Could not verify user'
                               })
    else:
        return ""

@app.route('/sign_up', methods=['POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        firstname = request.form['firstname']
        familyname = request.form['familyname']
        gender = request.form['gender']
        city = request.form['city']
        country = request.form['country']
        userObject = {
            'Email': email,
            'Password': password,
            'FirstName': firstname,
            'FamilyName': familyname,
            'Gender': gender,
            'City': city,
            'Country': country
        }
        status = db.addNewUser(userObject) ## add new user to database
        return json.dumps(status)
    else:
        return ""

@app.route('/getUserDataByEmail', methods=['POST'])
def getUserDataByEmail():
    if request.method == 'POST':
        email = request.form['email']
        searchEmail = request.form['searchUser']
        blob = request.form['blob']
        encMessage = request.form['hash']
        auth = verifyUser(email, encMessage, blob)
        if (auth['success']):
            status = db.getUserByEmail(auth['token'], searchEmail) ##get users profile info by email
            return json.dumps(status)
        else:
            return json.dumps({'success': False,
                               'message': 'Could not verify user'
                               })
    else:
        return ""

@app.route('/getUserDataByToken', methods=['POST'])
def getUserDataByToken():
    if request.method == 'POST':
        email = request.form['email']
        blob = request.form['blob']
        encMessage = request.form['hash']
        auth = verifyUser(email, encMessage, blob)
        if (auth['success']):
            status = db.getUserByToken(auth['token']) ##get users profile info by token
            #print(status)
            return json.dumps(status)
        else:
            return json.dumps({'success': False,
                               'message': 'Could not verify user'
                               })
    else:
        return ""

@app.route('/signOut', methods=['POST'])
def signOut():
    if request.method == 'POST':
        email = request.form['email']
        blob = request.form['blob']
        encMessage = request.form['hash']
        auth = verifyUser(email, encMessage, blob)
        if (auth['success']):
            status = db.delUserFromActive(auth['token'])
            ws = webSockets[auth['token']]
            ws.close()
            ##del webSockets[auth['token']]
            return json.dumps(status)
        else:
            return json.dumps({'success': False,
                               'message': 'Could not verify user'
                               })
    else:
        return ""

        ##kanske radera websocket TODO!!!!!!!!!!!!

@app.route('/changePassword', methods=['POST'])
def changePassword():
    if request.method == 'POST':
        email = request.form['email']
        oldpassword = request.form['oldpassword']
        newpassword = request.form['newpassword']
        blob = request.form['blob']
        encMessage = request.form['hash']
        auth = verifyUser(email, encMessage, blob)
        if (auth['success']):
            status = db.changePasswordForUser(auth['token'], oldpassword, newpassword)
            #print(status)
            return json.dumps(status)
        else:
            return json.dumps({'success': False,
                               'message': 'Could not verify user'
                               })
    else:
        return ""

@app.route('/postMessage', methods=['POST'])
def postMessage():
    if request.method == 'POST':
        email = request.form['email']
        toEmail = request.form['toEmail']
        message = request.form['message']
        encMessage = request.form['hash']
        blob = request.form['blob']
        auth = verifyUser(email, encMessage, blob)
        if (auth['success']):
            status = db.postMessageToEmail(auth['token'], message, toEmail)
            if db.checkLoggedInWithEmail(toEmail): ##if email signed in
                tokenToUpdate = db.emailToToken(toEmail) ## get token for user to log out
                print(tokenToUpdate)
                ws = webSockets[tokenToUpdate]
                dataObject = {"success": True,
                              "message": "Update chart"
                              }
                ws.send(json.dumps(dataObject)) ## send log out message to user
            return json.dumps(status)
        else:
            return json.dumps({'success': False,
                               'message': 'Could not verify user'
                               })
    else:
        return ""

def verifyUser(email, encryptedMessage, blob):
    token = db.emailToToken(email)
    blob = blob.encode('utf-8')
    verifyHash = hmac.new(bytes(token,'utf-8'), msg=blob, digestmod=hashlib.sha256).digest() ## hash users token with blob using sha256
    verifyHashDecoded = base64.standard_b64encode(verifyHash).decode('utf-8')
    if (verifyHashDecoded == encryptedMessage): ## if client and servers hash match
        return {'success': True,
                'token': token}
    else:
        return {'success': False}


@app.route('/getUserMessagesByEmail', methods=['POST'])
def getUserMessagesByEmail():
    if request.method == 'POST':
        fromEmail = request.form['fromEmail']
        email = request.form['email']
        encMessage = request.form['hash']
        blob = request.form['blob']
        auth = verifyUser(email, encMessage, blob)
        if (auth['success']):
            status = db.getMessagesByEmail(auth['token'], fromEmail)
            return json.dumps(status)
    else:
        return ""

@app.route('/getUserMessagesByToken', methods=['POST'])
def getUserMessagesByToken():
    if request.method == 'POST':
        email = request.form['email']
        encMessage = request.form['hash']
        blob = request.form['blob']
        auth = verifyUser(email, encMessage, blob)
        if (auth['success']):
            status = db.getMessagesByToken(auth['token'])
            return json.dumps(status)
        else:
            return json.dumps({'success': False,
                               'message': 'Could not verify user'
                               })
    else:
        return ""

@app.route('/getStats', methods=['POST'])
def getStats():
    if request.method == 'POST':
        email = request.form['email']
        encMessage = request.form['hash']
        blob = request.form['blob']
        auth = verifyUser(email, encMessage, blob)
        if (auth['success']):
            status = db.getStatsForUser(auth['token'])
            return json.dumps(status)
        else:
            return json.dumps({'success': False,
                               'message': 'Could not verify user'
                               })
    else:
        return ""


if __name__ == '__main__':
    print("running")
    app.run(debug=True)
