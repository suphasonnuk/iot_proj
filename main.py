from time import time
from django.shortcuts import render
from flask import Flask
import datetime, time
import pandas as pd
from flask import url_for, redirect, render_template, Response , request , session
import cv2
import os

app = Flask(__name__)

camera = cv2.VideoCapture(0)
camera.set(3,480)
camera.set(4,520)
camera.set(10,1000)

global capture,rec_frame, grey, switch, neg, face, rec, out
capture=0
grey=0
neg=0
face=0
switch=1
rec=0

admin = ''
_login = False
user_email = ""
user_name = ""
user_id = ""
user_year = 0
time_expected = ""
visiblility = ""

net = cv2.dnn.readNetFromCaffe('./saved_model/deploy.prototxt.txt', './saved_model/res10_300x300_ssd_iter_140000.caffemodel')


try:
    os.mkdir('./shots')
except OSError as error:
    pass

def detect_face(frame):
    global net
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
        (300, 300), (104.0, 177.0, 123.0))   
    net.setInput(blob)
    detections = net.forward()
    confidence = detections[0, 0, 0, 2]

    if confidence < 0.5:            
            return frame           

    box = detections[0, 0, 0, 3:7] * np.array([w, h, w, h])
    (startX, startY, endX, endY) = box.astype("int")
    try:
        frame=frame[startY:endY, startX:endX]
        (h, w) = frame.shape[:2]
        r = 480 / float(h)
        dim = ( int(w * r), 480)
        frame=cv2.resize(frame,dim)
    except Exception as e:
        pass
    return frame

def generate_frames():
    while True:
            
        ## read the camera frame
        success,frame=camera.read()
    
        frame = cv2.flip(frame, 1)
        if not success:
            break
        else:
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen_frames():  # generate frame by frame from camera
    global out, capture,rec_frame
    while True:
        success, frame = camera.read()
        if success:
            if(face):                
                frame= detect_face(frame)
            if(grey):
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if(neg):
                frame=cv2.bitwise_not(frame)    
            if(capture):
                capture=0
                now = datetime.datetime.now()
                p = os.path.sep.join(['shots', "{}_{}.png".format( user_id , str(now).replace(":",''))])
                cv2.imwrite(p, frame)
            
            if(rec):
                rec_frame=frame
                frame= cv2.putText(cv2.flip(frame,1),"Recording...", (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
                frame=cv2.flip(frame,1)
            
                
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
                
        else:
            pass

@app.route('/')
def index():
    return render_template("front.html" , id_visible = "hidden")

@app.route('/registering/')
def registering():
    return render_template("register.html")

@app.route('/register/' , methods  = ['POST' , 'GET'])
def register():
    global user_id, user_name , time_expected , years , visiblility ,  user_email
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user_id = request.form.get('user_id')
        years = request.form.get('user_year')
        time_expected = request.form.get('user_time')
        user_email = request.form.get('user_email') 
        visiblility = "hidden"
    return render_template("register.html")


@app.route('/home/' , methods = ['POST' , 'GET'])
def home():
    return redirect(url_for("index"))

@app.route('/main/' , methods = ['POST' , 'GET'])
def main():
    return render_template("index.html" , id_visible = "hidden")

@app.route('/history/' , methods = ['POST' , 'GET'])
def history():
    if (_login):
        return render_template("history.html")
    else:
        return render_template("login.html")


@app.route('/que/', methods = ['POST' , 'GET'])
def que():
    if (_login):
        if (admin):
            return render_template("que.html")     
    else:
        return render_template("login.html")


@app.route('/video')
def video():
    return Response(generate_frames() , mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    global user_id, user_name , time_expected , years , visiblility , _login
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user_id = request.form.get('user_id')
        years = request.form.get('years')
        time_expected = request.form.get('user_time')
        _login = True
        visiblility = "hidden"
        face_visibility = visiblility

        return render_template("index.html" , name = user_name , id = user_id , year = years ,time = time_expected , visible = face_visibility , id_visible = "")

@app.route('/login_page/', methods = ['POST' , 'GET'])
def login_page():
    if (_login):

        return render_template("Dashboard.html" , user_name = user_name , user_id = user_id)     
    else:
        return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)