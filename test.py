
from flask import Flask, render_template, Response, request
import numpy as np


app = Flask(__name__)
 
 
 
@app.route('/')
def index():
    return render_template('history.html')
    
  
if __name__ == '__main__':
    app.run('0.0.0.0', port = 5000 , debug=True)
