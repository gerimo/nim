#    To create a service account and have your application use it for API
#    access, run:
#        $ gcloud iam service-accounts create my-account
#        $ gcloud iam service-accounts keys create key.json
#          --iam-account=my-account@my-project.iam.gserviceaccount.com
#        $ export GOOGLE_APPLICATION_CREDENTIALS=key.json
#        $ ./my_application.sh

#    To temporarily use your own user credentials, run:
#        $ gcloud auth application-default login


# to connect to the instance $ gcloud compute ssh neemfs
# to initiate in productive $ sudo reboot / sudo service apache2 stop / sudo python app.py &
# before deploying to the server read this: https://cloud.google.com/compute/docs/access/create-enable-service-accounts-for-instances

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from flask import Flask, redirect, url_for, request, render_template, send_from_directory
# if you are using G Cloud remember to $ cp /etc/mongodb.conf /etc/mongod.conf
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename


# for google speech
# play -r 8000 -b 16 -c 1 -e signed [226612700]_[226612700]_[30-03-2017]_[16-48-00].raw
#in production install the following python google cloud version: pip install --upgrade google-cloud==0.24.0 --user
from google.cloud import speech
import time
import io
#install sox using apt-get install sox and pip install sox --user
import sox

# for google cloud storage
#https://cloud.google.com/appengine/docs/standard/python/googlecloudstorageclient/read-write-to-cloud-storage
#https://cloud.google.com/appengine/docs/standard/python/googlecloudstorageclient/setting-up-cloud-storage
import gcs_oauth2_boto_plugin
import boto
import shutil
import StringIO
import tempfile

#./google-cloud-sdk/.install
#./google-cloud-sdk/bin/gcloud init
# gcloud auth login
#!/usr/bin/python
#for google storage
from gcs_oauth2_boto_plugin.oauth2_helper import SetFallbackClientIdAndSecret
CLIENT_ID = '455316581334-irn49vs4uscp0tj4q7pb80dc79i11o4k.apps.googleusercontent.com'
CLIENT_SECRET = 'rs7wVFzTSFbgmuM0ZFMjdWh5'
OAUTH2_CLIENT_ID = '455316581334-irn49vs4uscp0tj4q7pb80dc79i11o4k.apps.googleusercontent.com'
OAUTH2_CLIENT_SECRET = 'rs7wVFzTSFbgmuM0ZFMjdWh5'
#gcs_oauth2_boto_plugin.SetFallbackClientIdAndSecret(CLIENT_ID, CLIENT_SECRET)

# URI scheme for Cloud Storage.
GOOGLE_STORAGE = 'gs'
# URI scheme for accessing local files.
LOCAL_FILE = 'file'

#The DB connection will assume that the database has the same name as the Flask Appliction which is "app"
app = Flask(__name__)
mongo = PyMongo(app)

UPLOAD_FOLDER = './uploads' #'gs://neemfs/'
ALLOWED_EXTENSIONS = set(['raw','flac','mp3','wav'])
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
            file_path_name, file_extension = os.path.splitext('./uploads/'+filename)
            if file_extension != '.raw':
                tfm = sox.Transformer()
                tfm.build(app.config['UPLOAD_FOLDER']+'/'+filename, os.path.splitext(file_path_name)[0]+'.raw')
                filename=os.path.splitext(filename)[0]+'.raw'#pero con raw
            print filename 
            print app.config['UPLOAD_FOLDER']
            #Al archivo ya esta grabado en ./uploads        
            #return redirect(url_for('uploaded_file',filename=filename))
            #file_path_name, file_extension = os.path.splitext(filename)
            #if file.file_extension != '.raw'
            #    tfm = sox.Transformer()
            #    tfm.build(file_name+file_extension, file_name+'.raw')
            #name = "[226612700]_[226612700]_[30-03-2017]_[16-48-00].flac"
            #filename = "./uploads/"+name
            #file_name, file_extension = os.path.splitext(filename)
            


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

# Para login de usuario
@app.route('/username')
def user_profile():
    user = mongo.db.users.find_one_or_404({'name': "Phonaroid.com"})
    return render_template('user.html',
        user=user)

# Code for testing google speech transcripts
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

# Code for file uploads to google storage

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS    

@app.route('/up', methods=['GET', 'POST'])
def up():
    UPLOAD_FOLDER = 'gs://neemfs/' #'gs://neemfs/'
    ALLOWED_EXTENSIONS = set(['raw','flac','mp3','wav'])
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
            file_path_name, file_extension = os.path.splitext('./uploads/'+filename)
            if file_extension != '.raw':
                tfm = sox.Transformer()
                tfm.build(app.config['UPLOAD_FOLDER']+'/'+filename, os.path.splitext(file_path_name)[0]+'.raw')
                filename=os.path.splitext(filename)[0]+'.raw'#pero con raw
            print filename 
            print app.config['UPLOAD_FOLDER']
            #Al archivo ya esta grabado en ./uploads        
            #return redirect(url_for('uploaded_file',filename=filename))



@app.route('/transcripts/<file_name>')
def transcript(file_name):
    transcript = mongo.db.transcripts.find({'file_name':file_name})
    return render_template('transcript.html', transcript=transcript)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)


#sudo gcloud auth login
#to copy the ssh keys gcloud compute copy-files ~/.ssh/neem.json neemfs:~/.ssh/neem.json --zone asia-east1-a
#mongo fast commenads / mongo / use app / db.users.find()