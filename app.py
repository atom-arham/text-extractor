from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import cv2
from PreProcess import File, Process
import pytesseract
from PIL import Image
import atexit, shutil

app = Flask(__name__)

def clean_up():
    folder = 'static/'
    for filename in os.listdir(folder):
        if filename.startswith('upload'):
            file_path = os.path.join(folder,filename)
            try:
                os.remove(file_path)
                print("File has been deleted")
            except Exception as e:
                print("Unable to delete file")

@app.route('/', methods=['GET','POST'])
def upload_file():
    file_name = None
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            ext = os.path.splitext(file.filename)[1]
            file_name = 'upload'+ ext
        
            file.save(os.path.join('static/',file_name))
    if not file_name:
        file_name = File().image_name
    return render_template('index.html', filename=file_name)

@app.route("/start", methods=['POST'])
def start():
    text = process()
    file_name = File().image_name
    return render_template('index.html', status_message=text,filename=file_name)

def process():
    process = Process()
    image = process.read()
    image = process.deskew(image)
    image = process.grayScale(image)
    #image = process.invert(image)
    image = process.thresholdBinary(image,maxt=255,block=11)

    raw = pytesseract.image_to_string(image)

    text = raw.split("\n")
    string = " ".join(text)
    para = "\n".join(text)
    return para

if __name__ == '__main__':
    clean_up()
    app.run(debug=True)
    
