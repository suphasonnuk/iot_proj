from time import time
from django.shortcuts import render
from flask import Flask
import datetime, time
import pandas as pd
import numpy as np
from flask import url_for, redirect, render_template, Response , request , session , flash , get_flashed_messages
import os
import datetime
import mysql.connector 
import hashlib




app = Flask(__name__)

db = mysql.connector.connect(host="localhost",username="root",password = '',database='license_plate_rec')
db_cur = db.cursor()
query_cur = db.cursor()

app.secret_key = "abc"  

def pwd_encoding(password): 
    md5_pass = hashlib.md5(password.encode())
    return md5_pass.hexdigest()

def load_plate(user_id):
    # print("loading plates...")
    get_plates = ("SELECT car_license_str FROM data_car WHERE user_id = %s")
    query_cur.execute(get_plates,[user_id])
    plates = query_cur.fetchall()
    return plates
def get_all_data():
    get_all_user = ("SELECT user_id,user_name,house_num,user_email FROM data_user")
    query_cur.execute(get_all_user)
    all_user = query_cur.fetchall()
    get_all_plates = ("SELECT data_user.user_name,data_car.car_license_str FROM data_user JOIN data_car ON data_car.user_id = data_user.user_id")
    query_cur.execute(get_all_plates)
    all_plates = query_cur.fetchall()
    return all_user,all_plates


login_id = None
login_name = None
login_role  = None
login_email = None
login_house = None
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
    # global user_id, user_name , time_expected , user_password , visiblility ,  user_email , data_recieved
    if request.method == 'POST':

        if ((request.form.get('user_name') == "") or (request.form.get('house_num') == "") or (request.form.get('user_password') == "") or (request.form.get('user_email') == "")):
            flash("Please fill out every information before going forward.")
            return redirect(url_for("registering"))

        else:
            #request for plates files.
            uploaded_file = request.files['user_lisense']
            if uploaded_file.filename != '':
                os.chdir(os.path.join( os.path.join(os.getcwd() , "shots")))
                ext = os.path.splitext(uploaded_file.filename)[-1].lower()
                
                if ext == ".jpg" or ".png":
                    uploaded_file.save(uploaded_file.filename)

            user_query = ("SELECT 'user_name' FROM data_user WHERE user_name = (%s)")
            query_cur.execute(user_query,[request.form.get('user_name')])
            users = query_cur.fetchall()
            if len(users) == 0:
                #execute db command add data to db
                user_data = [request.form.get('user_name'),pwd_encoding(request.form.get('user_password')),request.form.get('house_num'),request.form.get('user_email'),2]
                add_user_data = ("INSERT INTO data_user (user_name,user_password,house_num,user_email,role_id) VALUES (%s,%s,%s,%s,%s)")
                db_cur.execute(add_user_data,user_data)
                db.commit()
                return render_template("regis_suc.html")
            else: 
                flash("This username is already used")
                return render_template("register.html")
            
    if request.method == 'GET':
        return render_template("register.html")

    return render_template("register.html")

@app.route('/admin_delete_plate/' , methods = ['POST' , 'GET'])
def admin_delete_plate():
    if request.method == "POST":
        data = request.form.get('plate_delete') 
        delete_user = ("DELETE FROM data_car WHERE car_license_str = %s")
        db_cur.execute(delete_user,[data])
        add_log=("INSERT INTO user_log (user_id,user_action,user_time_stamp) VALUES (%s,%s,CURRENT_TIMESTAMP)")
        log_data = [login_id,"delete plate \'"+data+"\'"]
        db_cur.execute(add_log,log_data) 
        db.commit()
    return redirect(url_for("edit"))

@app.route('/delete_account/' , methods = ['POST' , 'GET'])
def delete_account():
    if request.method == "POST":
        delete_account = ("DELETE FROM data_user WHERE user_name = %s")
        db_cur.execute(delete_account,[request.form.get("button-name")])
        add_log=("INSERT INTO user_log (user_id,user_action,user_time_stamp) VALUES (%s,%s,CURRENT_TIMESTAMP)")
        log_data = [login_id,"Delete user \'"+request.form.get("button-name")+"\'"]
        db_cur.execute(add_log,log_data)
        db.commit()
    return redirect(url_for("edit"))

@app.route('/admin_add_plate/' , methods = ['POST' , 'GET'])
def admin_add_plate():
    if request.method == "POST":
        get_user_id = ("SELECT user_id FROM data_user WHERE user_name = %s")
        query_cur.execute(get_user_id,[request.form.get("button-name-license")])
        user_id = query_cur.fetchall()
        add_plate = ("INSERT INTO data_car (user_id,car_license_str) VALUES (%s,%s)") 
        data_add = [user_id[0][0],request.form.get("button_license")] 
        db_cur.execute(add_plate,data_add)
        add_log=("INSERT INTO user_log (user_id,user_action,user_time_stamp) VALUES (%s,%s,CURRENT_TIMESTAMP)")
        log_data = [login_id,"Add plate"+request.form.get("button_license")+"to user \'"+request.form.get("button-name-license")+"\'"]
        db_cur.execute(add_log,log_data)
        db.commit()
    return redirect(url_for("edit"))


@app.route('/history/' , methods = ['GET','POST'])
def history():
    global login_role,_login
    if(login_role == "admin" and _login == True):
        get_log_data = ("SELECT user_log.user_id,data_user.user_name,user_log.user_action,user_log.user_time_stamp FROM user_log JOIN data_user ON user_log.user_id = data_user.user_id")
        query_cur.execute(get_log_data)
        result = query_cur.fetchall()
        return render_template("history.html",logger = result )
    else:
        _login = False
        return render_template("login_error.html")
@app.route('/gate_history/', methods = ['GET','POST'])
def gate_history():
    global login_role,_login 
    if(login_role == "admin" and _login == True):
        print("access to gate history")
        get_gate_log_data = ("SELECT data_user.user_name,data_car.car_license_str,gate_log.gate_action,gate_log.gate_time_stamp FROM gate_log JOIN data_car ON gate_log.car_id = data_car.car_id JOIN data_user ON data_car.user_id = data_user.user_id")
        query_cur.execute(get_gate_log_data)
        result = query_cur.fetchall()
        print(result)
        return render_template("gate_history.html",gate_log = result)
    else:
        _login = False
        return render_template("login_error.html")

@app.route('/logout/' , methods = ['POST' , 'GET'])
def logout():
    global _login , data_use,login_id
    add_log=("INSERT INTO user_log (user_id,user_action,user_time_stamp) VALUES (%s,%s,CURRENT_TIMESTAMP)")
    log_data = [login_id,"logout"]
    db_cur.execute(add_log,log_data)
    db.commit()
    _login = False
    data_use = None
    return redirect(url_for("login_page"))


@app.route('/home/' , methods = ['POST' , 'GET'])
def home():
    global _login
    _login = False
    return redirect(url_for("index"))

@app.route('/edit/' , methods = ['POST' , 'GET'])
def edit():
    all_users,all_plates = get_all_data()
    if request.method == "POST":
        
        print(request.form.get("button-name"))
        print(request.form.get("add_name"))
        print(request.form.get("button_license"))
        print(request.form.get("plate_delete"))

        print(">>>>>>>>>>>>>>>>>>>>>>>>")
        print(request.form.get("button-name-license"))
    return render_template("admin_edit.html" , personal = all_users, _plates = all_plates)


@app.route('/add_plate/' , methods = ['POST' , 'GET'])
def add_plate():
    global plates,login_id
    print(login_id)
    if request.method == "POST":
        plates = load_plate(login_id)
        plate = request.form.get("add_plate")
        print(plates)
        if (plate,) not in plates:
            insert_plate = ("INSERT INTO data_car (user_id,car_license_str) VALUES (%s,%s)") 
            insert_data = [login_id,plate]
            db_cur.execute(insert_plate,insert_data)
            add_log=("INSERT INTO user_log (user_id,user_action,user_time_stamp) VALUES (%s,%s,CURRENT_TIMESTAMP)")
            log_data = [login_id,"add plate \'"+plate+"\'"]
            db_cur.execute(add_log,log_data)
            db.commit() 
            print("add plates successfully")
            plates = load_plate(login_id)
            return render_template("Dashboard.html" , user_name = login_name,house_num = login_house,user_email = login_email, _plates = plates)
        else:
            print("this run")
            flash("You already added that plate")
            return render_template("Dashboard.html" , user_name = login_name,house_num = login_house,user_email = login_email, _plates = plates)
    else:
        return render_template("Dashboard.html" , user_name = login_name,house_num = login_house,user_email = login_email, _plates = plates)

@app.route('/delete_plate/' , methods = ['POST' , 'GET'])
def delete_plate():
    plates = load_plate(login_id)
    if request.method == "POST": 
        data = request.form.get('delete_plate') 
        delete_user = ("DELETE FROM data_car WHERE car_license_str = %s")
        db_cur.execute(delete_user,[data])
        add_log=("INSERT INTO user_log (user_id,user_action,user_time_stamp) VALUES (%s,%s,CURRENT_TIMESTAMP)")
        log_data = [login_id,"delete plate \'"+data+"\'"]
        db_cur.execute(add_log,log_data) 
        db.commit()
        plates = load_plate(login_id)
        return render_template("Dashboard.html" , user_name = login_name,house_num = login_house,user_email = login_email, _plates = plates)     
    else:
        return render_template("Dashboard.html" , user_name = login_name, house_um = login_house,user_email = login_email,_plates = plates)     
    
    


@app.route('/admin_page/', methods = ['POST' , 'GET'])
def admin_page():
    global login_role,_login
    if (_login):
        if (login_role == "admin"):
            all_users,all_plates = get_all_data()
            return render_template("admin_page.html" , personal = all_users, _plates = all_plates)  
        else:
            _login = False
            return render_template("login_error.html")
    else:
        return render_template("login_error.html")


@app.route('/login/', methods=['GET', 'POST'])
def login():

    global visiblility , _login , data_use,login_id,login_role,login_name,login_email,login_house
    if request.method == 'POST':
        chk_login = ("SELECT * FROM data_user JOIN data_role ON data_role.role_id = data_user.role_id WHERE user_name = %s AND user_password = %s")
        get_user = [request.form.get("user_name"),pwd_encoding(request.form.get("user_password"))]
        query_cur.execute(chk_login,get_user) 
        login_result = query_cur.fetchall()
        if (len(login_result) != 0):
            flash("log in successful")
            login_id =  login_result[0][0]
            login_name = login_result[0][1]
            login_role = login_result[0][7]
            login_house = login_result[0][3]
            login_email = login_result[0][4]
            add_log=("INSERT INTO user_log (user_id,user_action,user_time_stamp) VALUES (%s,%s,CURRENT_TIMESTAMP)")
            log_data = [login_id,"login"]
            db_cur.execute(add_log,log_data)
            db.commit()
            _login = True
            plates = load_plate(login_id)
            return render_template("Dashboard.html" ,user_name = login_name, house_num = login_house,user_email = login_email, _plates = plates)
        else:
            flash("Please check your username and password, try again.")
            return render_template("login.html")

    if request.method == "GET":
            
            return render_template("login.html")



@app.route('/login_page/', methods = ['POST' , 'GET'])
def login_page():
    global  visiblility , _login,login_name,login_house,login_email,login_id
    if (_login):
        plates = load_plate(login_id)
        return render_template("Dashboard.html" , user_name = login_name,house_num=login_house,user_email=login_email, _plates = plates)     
    else:
        return render_template("login.html")

if __name__ == "__main__":
    app.run('0.0.0.0', port = 5000 , debug=True)
    db.close 