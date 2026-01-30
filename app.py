from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from PreProcess import File, Process

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])

def upload_file():
    if request.method == 'POST':
        file = request.files['file']

        ext = os.path.splitext(file.filename)[1]
        file_name = 'upload'+ ext
        
        file.save(os.path.join('static/',file_name))
        return render_template('index.html',filename= file_name, secure_filename=secure_filename(file_name))
    return render_template('index.html')

@app.route("/start", methods=['POST'])
def start():
    if request.method == 'POST':
        print("STARTED")
    return 

app.run(debug=True)