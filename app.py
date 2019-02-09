import time
import json

import flask
from flask import Flask, render_template
from flask import jsonify
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
from flask import request

import numpy as np
from imutils.perspective import four_point_transform
from imutils import contours
import imutils
import cv2
import argparse
from imutils.object_detection import non_max_suppression
from imutils.perspective import four_point_transform



app = Flask(__name__)
cors = CORS(app)
api = Api(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/page')
def index():
    return render_template('index1.html')

#the main function
def send_data():
    




@app.route('/monitor',)
@cross_origin()
def watch():
        while True:
             #   data = meter_result()
                display_data = send_data()
                response = app.response_class(
                        response=json.dumps(display_data),
                        status=200,
                        mimetype='application/json'
                )
                return response

if __name__ == "__main__":
        app.run(host='localhost', port=8080, debug=True)





