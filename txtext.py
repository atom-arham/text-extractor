from flask import Flask, render_template, Response
import cv2
import numpy as np
import easyocr

app = Flask(__name__)

def videoCapture():
    
    reader = easyocr.Reader(['en'], gpu=False)
    webcam = cv2.VideoCapture(0);

    webcam.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    webcam.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

    count = 0;
    result = []
    while True:
        ret,frame = webcam.read()
        if not ret:
            print("Can't get frame")
            break

        if frame is None:
            print("No frame")
            break

        if count % 30 == 0:
            low_res = cv2.resize(frame,(640,480))
            processed = processImage(low_res)

            language = reader.detect(processed)
            detected_language = language[0][0] if language else "unknown"

            result = reader.readtext(processed)

            print("Language: ",detected_language)

            
            
            
        count +=1
    
        for (bbox,text,prob) in result:

            (top_left,top_right,bottom_right,bottom_left) = bbox

            int_tl = (int(top_left[0]), int(top_left[1]))
            int_br = (int(bottom_right[0]),int(bottom_right[1]))
         
            cv2.rectangle(frame, int_tl,int_br,(0,255,0),2)
            cv2.putText(frame,text,(int_tl[0],int_tl[1]-10), cv2.FONT_HERSHEY_PLAIN,1.5,(0,255,0),2)
            
        ret,jpg = cv2.imencode('.jpg',frame)
        if not ret:
            continue

        frameToBytes = jpg.tobytes()
        yield (b'--frame\r\n' 
               b'Content-Type: image/jpeg\r\n\r\n'+ frameToBytes+b'\r\n')
            
def grayScale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
def gaussianBlur(image):
    return cv2.GaussianBlur(image,(5,5),0)

def adaptiveThreshold(image):
    return cv2.adaptiveThreshold(image,255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,11,2)

def processImage(image):
    image = grayScale(image);
    #image = gaussianBlur(image);
    image = adaptiveThreshold(image);
    return image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(videoCapture(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)