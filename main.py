from django.shortcuts import render
from flask import Flask
import pandas as pd
from flask import url_for, redirect, render_template, Response
import cv2

app = Flask(__name__)

camera = cv2.VideoCapture(0)
camera.set(3,480)
camera.set(4,520)
camera.set(10,1000)

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

@app.route('/' )
def index():
    return render_template("index.html")

@app.route('/home/' , methods = ['POST' , 'GET'])
def home():
    return redirect(url_for("index"))

@app.route('/history/' , methods = ['POST'])
def history():
    return render_template("history.html")


@app.route('/que/', methods = ['POST' , 'GET'])
def que():
    return render_template("que.html")


@app.route('/video')
def video():
    return Response(generate_frames() , mimetype='multipart/x-mixed-replace; boundary=frame')




if __name__ == "__main__":
    app.run(debug=True)