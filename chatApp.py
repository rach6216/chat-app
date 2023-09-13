from flask import Flask, render_template,request,redirect,url_for,session
import csv
import os
import base64
from enum import Enum
import datetime
from flask_session import Session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
 
# Fetch the rooms names from DB
def get_rooms_names():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT Roomname FROM Rooms')
    rooms = cursor.fetchone()
    return rooms


# Fetch the rooms names from DB
def get_users_details():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Users')
    users_de = cursor.fetchone()
    return users_de

#Check if user exist and compare passwords
def check_if_user_exists(username, password):
    user_data=get_users_details()
    for row in user_data:
            name, pws= row[0],row[1] 
            if name == username:
                if decode_password(pws) == password:
                   return 1,"user and password are correct"
                else:
                    return 2,"User name already exists"
    return 3,"new user"

#Add user to users table
def add_user(username,password):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO Users(Username,Password) VALUES (%s,%s)',(username,password))
    user = mysql.connection.commit()

# create new room 
def create_a_room(room,username):
    if room not in get_rooms_names():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO Rooms(Roomname) VALUES (%s)',(room))
        roomID = mysql.connection.commit()
        cursor.execute('INSERT INTO Messages(Timestamp,RoomID,Username,Message) VALUES (%s)',(datetime.datetime.now().strftime("[%d/%m/%Y %H:%M:%S]"),roomID,username,'Wellcom To {} room!'.format(room)))
        mysql.connection.commit()
    else:
        print("The room name is already exist")
        

class user_status(Enum):
    PASS_AND_NAME_MATCH = 1
    NAME_MATCH = 2
    NO_MATCH = 3
    ERROR = 4

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234567890'
app.config['MYSQL_DB'] = 'chat-app-db'
mysql = MySQL(app)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'your_secret_key!!!!'

Session(app)


class user_status(Enum):
    PASS_AND_NAME_MATCH = 1
    NAME_MATCH = 2
    NO_MATCH = 3
    ERROR = 4

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'your_secret_key!!!!'

Session(app)

@app.route('/',methods=['GET','POST'] )
def homePage():
    return redirect("/register") 
    

@app.route('/register',methods=['GET','POST'] )
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        status,msg = check_if_user_exists(username,password)
        if status == user_status.NO_MATCH.value:
           add_user(username,encode_password(password))
           return redirect("/login")
        elif status == user_status.NAME_MATCH.value:
           return msg
        elif status == user_status.PASS_AND_NAME_MATCH.value:
            return redirect("/login") 
    else:
        return render_template('register.html')
    

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        status,msg=check_if_user_exists(username,password)
        if status == user_status.PASS_AND_NAME_MATCH.value:
            session['user_name'] = username
            session['user_password'] = password
            return redirect("/lobby") 
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/lobby', methods=['GET','POST'])
def lobby():
    if not session.get("user_name"):
        return redirect("/")
    if request.method == 'POST':
        create_a_room(request.form['new_room'])
    else:
        enter_room(request.args.get('room'))
    return render_template('lobby.html', room_names=get_rooms_names())
     

def enter_room(room):
    return render_template('chat.html',room=room)


@app.route('/logout', methods=['GET','POST'])
def logOut():
    session.pop('user_name', 'user_password')
    return redirect('login')

@app.route('/chat/<room>', methods=['GET','POST'])
def chat_room(room):
    if not session.get("user_name"):
        return redirect("/")
    # Display the specified chat room with all messages sent
    return render_template('chat.html',room=room)

@app.route('/api/clear/<room>', methods=['POST','GET'])
def clear_room_data(room):
    if not session.get("user_name"):
        return redirect("/")
    filename = os.getenv('ROOMS_DIR')+room+".txt"
    with open(filename, "wb") as file: 
        file.truncate(0)      
        file.close() 
    return "success" 

@app.route('/api/chat/<room>', methods=['GET','POST'])
def updateChat(room):
    if not session.get("user_name"):
        return redirect("/")
    filename = os.getenv('ROOMS_DIR')+room+".txt"
    if request.method == 'POST':
        msg = request.form['msg']
        if "user_name" in session:
            # Get the current date and time
            # current_datetime = datetime.datetime.now()
            # Format the date and time as a string
            formatted_datetime = datetime.datetime.now().strftime("[%d/%m/%Y %H:%M:%S]")
            with open(filename,"a") as file:
                file.write("\n"+formatted_datetime+"   "+session.get('user_name')+": "+msg)
    with open(filename,"r") as file:
        room_data = file.read()
        return room_data


def encode_password(password):
    pass_bytes = password.encode('ascii')
    base64_bytes = base64.b64encode(pass_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message

def decode_password(password):
    base64_bytes = password.encode('ascii')
    pass_bytes = base64.b64decode(base64_bytes)
    password = pass_bytes.decode('ascii')
    return password




if __name__ == '__main__':
   app.run(host="0.0.0.0")

