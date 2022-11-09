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

# def load_plate():
#     print("loading plates")
#     plates_list = []

# data_use = None
# license_img = None

# user_plates = []
# user_email = []
# error = None
# user_password = []
# grey=0
# neg=0
# face=0
# switch=1
# rec=0
# plates = pd.DataFrame({
#             "user_name" : user_name,
#             "user_plates" : user_plates,
#         })
# data_recieved = pd.DataFrame({
#             "user_name" : user_name,
#             "user_id" : user_id,
#             "user_password" : user_password,
#             "user_email" : user_email
#         ,})


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

@app.route('/delete_names/' , methods = ['POST' , 'GET'])
def delete_names():
    global _login , data_use
    delete_user = ("DELETE FROM data_user WHERE  user_name = %s")
    usr2del = [request.form.get('user_name')]
    db_cur.execute(delete_user,usr2del)
    db.commit()
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
        ## add plate here

        if request.form.get("add_plate") not in plates.loc[plates["user_name"] == data_use[0][0] , "user_plates"].values:
            user_plates.append(request.form.get("add_plate"))
            plates = pd.concat([plates, _plates])
            plates.index = range(len(user_plates))


            return render_template("Dashboard.html" , user_name = login_name,house_num = login_house,user_email = login_email,personal = data_use[0], _plates = plates.loc[plates['user_name'] == data_use[0][0]].values.tolist())
        flash("You already added that plate")
        return render_template("Dashboard.html" , user_name = login_name,house_num = login_house,user_email = login_email,personal = data_use[0], _plates = plates.loc[plates['user_name'] == data_use[0][0]].values.tolist())

    else:
        return render_template("Dashboard.html" , user_name = login_name,house_num = login_house,user_email = login_email,personal = data_use[0], _plates = plates.loc[plates['user_name'] == data_use[0][0]].values.tolist())

@app.route('/delete_plate/' , methods = ['POST' , 'GET'])
def delete_plate():

    if request.method == "POST": 
        data = request.form.get('delete_plate') 
        plate_seleted = data
        # user_plates.remove(data)
        delete_user = ("DELETE FROM data_car WHERE  car_license_str = %s")
        # usr2del = (request.form.get('delete_plate'))
        db_cur.execute(delete_user,data)
        db.commit()
        plates.drop(plates[plates["user_plates"] == plate_seleted].index , inplace=True)
        
        return render_template("Dashboard.html" , user_name = login_name,house_num = login_house,user_email = login_email, personal = data_use[0] , _plates = plates.loc[plates['user_name'] == data_use[0][0]].values.tolist())     
    else:
        return render_template("Dashboard.html" , user_name = login_name, personal = data_use[0] ,
         _plates = plates.loc[plates['user_name'] == data_use[0][0]].values.tolist())     
    
    


@app.route('/admin_page/', methods = ['POST' , 'GET'])
def admin_page():
    global login_role
    if (_login):
        if (login_role == "admin"):
            return render_template("admin_page.html" , personal = "", _plates = plates.values.tolist())  
        else:
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
        login_result = login_result[0]
        if (len(login_result) != 0):
            flash("log in successful")
            login_id =  login_result[0]
            login_name = login_result[1]
            login_role = login_result[7]
            login_house = login_result[3]
            login_email = login_result[4]
            add_log=("INSERT INTO user_log (user_id,user_action,user_time_stamp) VALUES (%s,%s,CURRENT_TIMESTAMP)")
            log_data = [login_id,"login"]
            db_cur.execute(add_log,log_data)
            db.commit()
            _login = True
            return render_template("Dashboard.html" ,user_name = login_name, house_num = login_house,user_email = login_email, _plates = [])
        else:
            flash("Your user name is not in our DataBase, try again")

    if request.method == "GET":
            
            return render_template("login.html")



@app.route('/login_page/', methods = ['POST' , 'GET'])
def login_page():
    global  visiblility , _login,login_name,login_house,login_email
    if (_login):
        return render_template("Dashboard.html" , user_name = login_name,house_num=login_house,user_email=login_email, _plates = plates.loc[plates['user_name'] == data_use[0][0]].values.tolist())     
    else:
        return render_template("login.html")

if __name__ == "__main__":
    app.run('0.0.0.0', port = 5000 , debug=True)
    db.close 