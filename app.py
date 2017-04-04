import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from flask import Flask, redirect, url_for, request, render_template, send_from_directory
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename


# for google speech
# play -r 8000 -b 16 -c 1 -e signed [226612700]_[226612700]_[30-03-2017]_[16-48-00].raw
from google.cloud import speech
import time
import io

import boto
import gcs_oauth2_boto_plugin
import shutil
import StringIO
import tempfile

#./google-cloud-sdk/.install
#./google-cloud-sdk/bin/gcloud init
# gcloud auth login
#!/usr/bin/python
#for google storage
#from gcs_oauth2_boto_plugin.oauth2_helper import SetFallbackClientIdAndSecret
CLIENT_ID = '455316581334-irn49vs4uscp0tj4q7pb80dc79i11o4k.apps.googleusercontent.com'
CLIENT_SECRET = 'rs7wVFzTSFbgmuM0ZFMjdWh5'
OAUTH2_CLIENT_ID = '455316581334-irn49vs4uscp0tj4q7pb80dc79i11o4k.apps.googleusercontent.com'
OAUTH2_CLIENT_SECRET = 'rs7wVFzTSFbgmuM0ZFMjdWh5'
gcs_oauth2_boto_plugin.SetFallbackClientIdAndSecret(CLIENT_ID, CLIENT_SECRET)

# URI scheme for Cloud Storage.
GOOGLE_STORAGE = 'gs'
# URI scheme for accessing local files.
LOCAL_FILE = 'file'


#The DB connection will assume that the database has the same name as the Flask Appliction which is "app"
app = Flask(__name__)
mongo = PyMongo(app)

UPLOAD_FOLDER = './uploads' #'gs://neemfs/'
ALLOWED_EXTENSIONS = set(['pdf','mp3', 'mp3', '3ge', 'wev', 'flac', 'mov', 'raw'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/demo')
def demo():
    return render_template('demo.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS    

@app.route('/call_list', methods=['GET', 'POST'])
def upload_file():
    total = len(os.listdir('./uploads'))
    count = 0
    # generate list of available files already uploaded, to display on the view
    files = os.listdir('./uploads')
    # upload a new file to the view
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('uploaded_file',filename=filename))
            # Once the file has been stored in GS, we generate the transcript
            from google.cloud import speech
            hints = ['pantalla', 'iphone', '119', '69','bateria']
            client = speech.Client()
            file_name = "56995719043_56995719043_30-03-2017_14-31-19.raw"
            sample = client.sample(source_uri='gs://neemfs/'+file_name,
                        encoding=speech.Encoding.LINEAR16,
                        sample_rate=8000)
            operation = sample.async_recognize(language_code='es-CL',max_alternatives=2,speech_context=hints)
            retry_count = 100
            while retry_count > 0 and not operation.complete:
                retry_count -= 1
                time.sleep(10)
                operation.poll()  # API call
            operation.complete
            for result in operation.results:
                for alternative in result.alternatives:
                    print('=' * 20)
                    print(alternative.transcript)
                    print(alternative.confidence)
                    save = mongo.db.transcripts.insert({'file_name':file_name, 'content': {'text':alternative.transcript, 'confidence':alternative.confidence}})
                    transcript = mongo.db.transcripts.find({'file_name':file_name})
            return render_template('transcript.html',
        user=user, transcript=transcript)   


    return render_template('call_list.html', count = count, total = total, files = files)

# retrieve the audio
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

# view user prpfile        
@app.route('/user')
def user():
    user = mongo.db.users.find_one_or_404({'name': "Phonaroid.com"})
    return render_template('user.html',
        user=user)

@app.route('/new', methods=['POST'])
def new():
    item_doc = {
        'name': request.form['name'],
        'description': request.form['description']
    }
    db.tododb.insert_one(item_doc)
    return redirect(url_for('todo'))

# Para login de usuario
@app.route('/username')
def user_profile():
    user = mongo.db.users.find_one_or_404({'name': "Phonaroid.com"})
    return render_template('user.html',
        user=user)

# Grabacion del contenido del audio en la base de datos
@app.route('/speech')
def speech():
    from google.cloud import speech
    hints = ['pantalla', 'iphone', '119', '69','bateria']
    client = speech.Client()
    file_name = "[+56953645455]_[+56953645455]_[31-03-2017]_[14-30-46].raw"
    sample = client.sample(source_uri='gs://neemfs/'+file_name,
                        encoding=speech.Encoding.LINEAR16,
                        sample_rate=8000)
    operation = sample.async_recognize(language_code='es-CL',max_alternatives=2,speech_context=hints)
    retry_count = 100
    while retry_count > 0 and not operation.complete:
        retry_count -= 1
        time.sleep(10)
        operation.poll()  # API call
    operation.complete
    for result in operation.results:
        for alternative in result.alternatives:
            print('=' * 20)
            print(alternative.transcript)
            print(alternative.confidence)
            save = mongo.db.transcripts.insert({'file_name':file_name, 'content': {'text':alternative.transcript, 'confidence':alternative.confidence}})
            transcript = mongo.db.transcripts.find({'file_name':file_name})
    return render_template('transcript.html',
        user=user, transcript=transcript)

@app.route('/transcripts/<file_name>')
def transcript(file_name):
    transcript = mongo.db.transcripts.find({'file_name':file_name})
    return render_template('transcript.html', transcript=transcript)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1190, debug=True)
