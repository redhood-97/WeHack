import time
import json

import flask
from flask import Flask, render_template
from flask import jsonify
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api

import numpy as np
from imutils.perspective import four_point_transform
from imutils import contours
import imutils
import cv2



app = Flask(__name__)
cors = CORS(app)
api = Api(app)
app.config['CORS_HEADERS'] = 'Content-Type'
@app.route('/page')
def index():
    return render_template('index1.html')

def meter_result():
        DIGITS_LOOKUP = {
            (1, 1, 1, 0, 1, 1, 1): 0,
            (0, 0, 1, 0, 0, 1, 0): 1,
            (1, 0, 1, 1, 1, 0, 1): 2,
            (1, 0, 1, 1, 0, 1, 1): 3,
            (0, 1, 1, 1, 0, 1, 0): 4,
            (1, 1, 0, 1, 0, 1, 1): 5,
            (1, 1, 0, 1, 1, 1, 1): 6,
            (1, 0, 1, 0, 0, 1, 0): 7,
            (1, 1, 1, 1, 1, 1, 1): 8,
            (1, 1, 1, 1, 0, 1, 1): 9
        }

# load the example image
        image = cv2.imread("a2.jpg")
        digits = []
# pre-process the image by resizing it, converting it to
# graycale, blurring it, and computing an edge map
#image = imutils.resize(image, height=500)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 200, 255)

        xpos=[312, 835, 823, 307]
        ypos=[95, 108, 276, 260]

#xpos=[207, 972, 969, 195]
#ypos=[95, 102, 299, 284]
        pts = np.asarray([(xpos[0], ypos[0]), (xpos[1], ypos[1]), (xpos[2], ypos[2]), (xpos[3], ypos[3])])

        warped = four_point_transform(gray, pts)
        output = four_point_transform(image, pts)

# threshold the warped image, then apply a series of morphological
# operations to cleanup the thresholded image
        thresh = cv2.threshold(warped, 0, 255,
        cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
#thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

#cv2.imwrite('test2.jpg',thresh)
# find contours in the thresholded image, then initialize the
# digit contours lists
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        digitCnts = []

# loop over the digit area candidates
        for c in cnts:
    # compute the bounding box of the contour
            (x, y, w, h) = cv2.boundingRect(c)
    # if the contour is sufficiently large, it must be a digit
            if (w>20 and w <= 80) and (h >= 30 and h <= 150):
                    digitCnts.append(c)

        digitCnts = contours.sort_contours(digitCnts,
        method="left-to-right")[0]
        digits = []

        Cx = []
        Cy =[]
# compute the center of the contour
        for c in digitCnts:
                M = cv2.moments(c)
                Cx.append(int(M["m10"] / M["m00"]))
                Cy.append(int(M["m01"] / M["m00"]))
                counter =0

# loop over each of the digits
        while counter < len(Cx):
    # extract the digit ROI
                if counter+1 < len(Cx):
                        if abs(Cx[counter] - Cx[counter+1]) <10:
                                (x, y, w, h) = cv2.boundingRect(digitCnts[counter])
                                (x1, y1, w1, h1) = cv2.boundingRect(digitCnts[counter+1])
                                w = (x1+w1)-x
                                h = abs((y1-h1)-y)
                                counter = counter+2
                                roi = thresh[y1 - 4:y1 + h, x1 - 4:x1 + w]
                        else:
                                (x, y, w, h) = cv2.boundingRect(digitCnts[counter])
                                counter = counter + 1
                                roi = thresh[y:y + h, x:x + w]
                else:
                        (x, y, w, h) = cv2.boundingRect(digitCnts[counter])
                        counter = counter + 1
                        roi = thresh[y:y + h, x:x + w]


    # compute the width and height of each of the 7 segments
    # we are going to examine
        (roiH, roiW) = roi.shape
        (dW, dH) = (int(roiW * 0.15), int(roiH * 0.10))
    #(dW, dH) = (16,50)
        dHC = int(roiH * 0.03)

    # define the set of 7 segments
        segments = [
                ((0, 0), (w, dH)),  # top
                ((0, 0), (dW, h // 2)), # top-left
                ((w - dW, 0), (w, h // 2)), # top-right
                ((0, (h // 2) - dHC) , (w, (h // 2) + dHC)), # center
                ((0, h // 2), (dW, h)), # bottom-left
                ((w - dW, h // 2), (w, h)), # bottom-right
                ((0, h - dH), (w, h))   # bottom
        ]
        on = [0] * len(segments)

    # loop over the segments
        for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
        # extract the segment ROI, count the total number of
        # thresholded pixels in the segment, and then compute
        # the area of the segment
                segROI = roi[yA:yB, xA:xB]
                total = cv2.countNonZero(segROI)
                area = (xB - xA) * (yB - yA)
                print(total/float(area))
        # if the total number of non-zero pixels is greater than
        # 50% of the area, mark the segment as "on"
                if total / float(area) > 0.3:
                        on[i]= 1

    # lookup the digit and draw it on the image

    #    try:
        digit = DIGITS_LOOKUP[tuple(on)]
       # except:
        #        continue

        digits.append(digit)
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 0, 255), 1)
        cv2.putText(output, str(digit), (x - 10, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)

        print(digits)

        # PRIORITY CODE ---------------------------------------------->
        #cv2.imshow("Input", image)
        #cv2.imshow("Output", output)
        #cv2.imshow('thresh',thresh)
        cv2.waitKey(0)
        data = {
        
        #        "the_result" : digits
        }
        #return (digits)
        

        

@app.route('/monitor')
@cross_origin()
def watch():
        while True:
                data = meter_result()
                response = app.response_class(
                        response=json.dumps(data),
                        status=200,
                        mimetype='application/json'
                )
                return response

if __name__ == "__main__":
        app.run(host='localhost', port=8080, debug=True)





