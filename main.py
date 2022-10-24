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
admin = "suphason"
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

@app.route('/logout/' , methods = ['POST' , 'GET'])
def logout():
    global _login
    _login = 0
    return redirect(url_for("login_page"))


@app.route('/home/' , methods = ['POST' , 'GET'])
def home():
    return redirect(url_for("index"))

@app.route('/main/' , methods = ['POST' , 'GET'])
def main():
    return render_template("index.html" , id_visible = "hidden")

@app.route('/history/' , methods = ['POST' , 'GET'])
def history():
    if (_login):
        return render_template(" history.html")
    else:
        return render_template("login_error.html")


@app.route('/que/', methods = ['POST' , 'GET'])
def que():
    if (_login):
        if (data_use[0][0] == admin):
            return render_template("que.html")  
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
            return render_template("Dashboard.html" , name = user_name , id = user_id , visible = face_visibility , id_visible = "" , personal = data_use[0])
        else:

            flash("Your user name is not in our DataBase, try again")
            return render_template("login.html")

    if request.method == "GET":
            
            return render_template("login.html")



@app.route('/login_page/', methods = ['POST' , 'GET'])
def login_page():
    global user_id, user_name , user_password , years , visiblility , _login
    if (_login):

        return render_template("Dashboard.html" , user_name = user_name , user_id = user_id , personal = data_use[0])     
    else:
        return render_template("login.html")

if __name__ == "__main__":
    app.run('0.0.0.0', port = 80 , debug=True)