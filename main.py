from time import time
from django.shortcuts import render
from flask import Flask
import datetime, time
import pandas as pd
import numpy as np
from flask import url_for, redirect, render_template, Response , request , session , flash , get_flashed_messages
import cv2
import os
import datetime

app = Flask(__name__)


app.secret_key = "abc"  
current_time = datetime.datetime.now()

camera = cv2.VideoCapture(0)
camera.set(3,480)
camera.set(4,520)
camera.set(10,1000)

global capture,rec_frame, grey, switch, neg, face, rec, out


data_use = None
_admin = ["suphason" , "nont"]

license_img = None

user_plates = []
user_email = []
user_name = []
error = None
user_password = []
user_id = []
grey=0
neg=0
face=0
switch=1
rec=0

plates = pd.DataFrame({
            "user_name" : user_name,
            "user_plates" : user_plates,
        })

data_recieved = pd.DataFrame({
            "user_name" : user_name,
            "user_id" : user_id,
            "user_password" : user_password,
            "user_email" : user_email
        ,})



_login = False
visiblility = ""

@app.route('/')
def index():
    return render_template("front.html" , id_visible = "hidden")

@app.route('/registering/')
def registering():
    return render_template("register.html")

@app.route('/register/' , methods  = ['POST' , 'GET'])
def register():
    global user_id, user_name , time_expected , user_password , visiblility ,  user_email , data_recieved

    if request.method == 'POST':

        if ((request.form.get('user_name') == "") or (request.form.get('user_id') == "") or (request.form.get('user_password') == "") or (request.form.get('user_email') == "")):
            flash("Please fill out every information before going forward.")
            return redirect(url_for("registering"))

        else:

            uploaded_file = request.files['user_lisense']
            if uploaded_file.filename != '':
                os.chdir(os.path.join( os.path.join(os.getcwd() , "shots")))
                ext = os.path.splitext(uploaded_file.filename)[-1].lower()
                
                if ext == ".jpg" or ".png":
                    uploaded_file.save(uploaded_file.filename)

            _data_recieved = pd.DataFrame({
                "user_name" : [request.form.get('user_name')],
                "user_id" : [request.form.get('user_id')],
                "user_password" : [request.form.get('user_password')],
                "user_email" : [request.form.get('user_email')]
            })

            if request.form.get('user_name') not in user_name:
                user_name.append(_data_recieved['user_name'].values[0])
                user_id.append(_data_recieved['user_name'].values[0])
                user_password.append(_data_recieved['user_name'].values[0])
                user_email.append(_data_recieved['user_name'].values[0])
                visiblility = "hidden"

                data_recieved = pd.concat([data_recieved , _data_recieved])
                return render_template("regis_suc.html")
        
            
            else: 
                flash("This username is already used")
                return render_template("register.html")
            
    if request.method == 'GET':
        return render_template("register.html")

    return render_template("register.html")

@app.route('/delete_names/' , methods = ['POST' , 'GET'])
def delete_names():
    global _login , data_use
    _login = False

    data_use = None
    return redirect(url_for("login_page"))

@app.route('/delete_plates/' , methods = ['POST' , 'GET'])
def delete_plates():
    global _login , data_use
    _login = False

    data_use = None
    return redirect(url_for("login_page"))

@app.route('/logout/' , methods = ['POST' , 'GET'])
def logout():
    global _login , data_use
    _login = False

    data_use = None
    return redirect(url_for("login_page"))


@app.route('/home/' , methods = ['POST' , 'GET'])
def home():
    return redirect(url_for("index"))

@app.route('/edit/' , methods = ['POST' , 'GET'])
def edit():
    return render_template("admin_edit.html" , personal = data_recieved.values.tolist(), _plates = plates.values.tolist())


@app.route('/add_plate/' , methods = ['POST' , 'GET'])
def add_plate():
    global plates
    if request.method == "POST":
        _plates = pd.DataFrame({
            "user_name" : [data_use[0][0]],
            "user_plates" : [request.form.get("add_plate")],
        })

        if request.form.get("add_plate") not in plates.loc[plates["user_name"] == data_use[0][0] , "user_plates"].values:
            user_plates.append(request.form.get("add_plate"))
            plates = pd.concat([plates, _plates])
            plates.index = range(len(user_plates))


            return render_template("Dashboard.html" , personal = data_use[0], _plates = plates.loc[plates['user_name'] == data_use[0][0]].values.tolist())
        flash("You already added that plate")
        return render_template("Dashboard.html" , personal = data_use[0], _plates = plates.loc[plates['user_name'] == data_use[0][0]].values.tolist())

    else:
        return render_template("Dashboard.html" , personal = data_use[0], _plates = plates.loc[plates['user_name'] == data_use[0][0]].values.tolist())

@app.route('/delete_plate/' , methods = ['POST' , 'GET'])
def delete_plate():

    if request.method == "POST": 
        data = request.form.get('delete_plate') 
        plate_seleted = data
        user_plates.remove(data)
        plates.drop(plates[plates["user_plates"] == plate_seleted].index , inplace=True)
        
        return render_template("Dashboard.html" , user_name = user_name , 
        user_id = user_id , personal = data_use[0] , _plates = plates.loc[plates['user_name'] == data_use[0][0]].values.tolist())     
    else:
        return render_template("Dashboard.html" , user_name = user_name , user_id = user_id , personal = data_use[0] ,
         _plates = plates.loc[plates['user_name'] == data_use[0][0]].values.tolist())     
    
    


@app.route('/admin_page/', methods = ['POST' , 'GET'])
def admin_page():
    if (_login):
        if (data_use[0][0] in _admin):
            return render_template("admin_page.html" , personal = data_recieved.values.tolist() , _plates = plates.values.tolist())  
        else:
            return render_template("login_error.html")
    else:
        return render_template("login_error.html")

    
@app.route('/login/', methods=['GET', 'POST'])
def login():
    global user_id, user_name , user_password , years , visiblility , _login , error, data_use
    if request.method == 'POST':
        visiblility = "hidden"
        face_visibility = visiblility

        data_use = data_recieved[(data_recieved['user_name'] == request.form.get("user_name")) & ((data_recieved['user_password'] == request.form.get("user_password")))].values.tolist()
        if ( data_use != []):
            flash("log in successful")
            _login = True
            return render_template("Dashboard.html" , name = user_name , id = user_id , visible = face_visibility ,
             id_visible = "" , personal = data_use[0],  _plates = plates.loc[plates['user_name'] == data_use[0][0]].values.tolist())
        else:

            flash("Your user name is not in our DataBase, try again")
            return render_template("login.html")

    if request.method == "GET":
            
            return render_template("login.html")



@app.route('/login_page/', methods = ['POST' , 'GET'])
def login_page():
    global user_id, user_name , user_password , years , visiblility , _login
    if (_login):

        return render_template("Dashboard.html" , user_name = user_name , user_id = user_id , personal = data_use[0] , _plates = plates.loc[plates['user_name'] == data_use[0][0]].values.tolist())     
    else:
        return render_template("login.html")

if __name__ == "__main__":
    app.run('0.0.0.0', port = 80 , debug=True)