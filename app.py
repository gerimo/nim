import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from flask import Flask, redirect, url_for, request, render_template, send_from_directory
# if you are using G Cloud remember to $ cp /etc/mongodb.conf /etc/mongod.conf
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from BeautifulSoup import BeautifulSoup

# for google speech pip install --upgrade google-cloud==0.24.0 --user, please note that the application is unstable if you use 0.25 or higher you should rewrite the application with the following examples https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/speech/cloud-client/transcribe_async.py
import time
import io
#install sox using apt-get install sox and pip install sox --user and test the result # play -r 8000 -b 16 -c 1 -e signed [226612700]_[226612700]_[30-03-2017]_[16-48-00].raw
import sox

# Authentification for Google Speech $ --upgrade google-cloud-speech
from google.cloud import speech

#The DB connection will assume that the database has the same name as the Flask Appliction which is "app"
app = Flask(__name__)
mongo = PyMongo(app)
UPLOAD_FOLDER = os.getcwd()+'/uploads' #'gs://neemfs/'
ALLOWED_EXTENSIONS = set(['raw','flac','mp3','wav'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# URI scheme for Cloud Storage.
GOOGLE_STORAGE = 'gs'
# URI scheme for accessing local files.
LOCAL_FILE = 'file'

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
    gs = "gs://neem-fs.appspot.com/"
    files = os.listdir(UPLOAD_FOLDER)
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
                filename=os.path.splitext(filename)[0]+'.raw'
                os.system("gsutil cp ./uploads/"+filename+" "+gs+filename)
                print "does it?"
            #upload the file to gs    
            print filename 
            print app.config['UPLOAD_FOLDER']
            # Once the file has been stored in GS, we generate the transcript
            from google.cloud import speech
            client = speech.Client()
            hints = ['pantalla', 'iphone', '119', '69','bateria']
            sample = client.sample(content=None,source_uri=gs+filename,encoding='LINEAR16',sample_rate_hertz=8000)
            operation = sample.long_running_recognize(language_code='es-CL',max_alternatives=2, speech_contexts=hints)
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
                    save = mongo.db.transcripts.insert({'filename':filename, 
                        'content': {'text':alternative.transcript, 'confidence':alternative.confidence,
                        'verified':0}})
                    transcript = mongo.db.transcripts.find({'filename':filename})
            return render_template('transcript.html',user=user, transcript=transcript) 
    return render_template('call_list.html', files=files)
            
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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS    

@app.route('/transcripts/<filename>')
def transcript(filename):
    transcript = mongo.db.transcripts.find({'filename':filename}) 
    return render_template('transcript.html', transcript=transcript)

@app.route('/case/create', methods=['GET', 'POST'])
def case():
    if request.method == 'POST':   
       # save = mongo.db.cases.insert({'name':request.form['name'], 
       #                 'keywords': {'identify': request.form['identify'], 'successful': request.form['successful'],  
       #                 'mistaken': request.form['mistaken']}
       #                 })
        save = mongo.db.cases.insert({'name':request.form.get('name'), 
                        'keywords': {'identify': request.form.get('identify'), 'successful': request.form.get('successful'),  
                        'mistaken': request.form.get('mistaken')}
                        })
        #case = mongo.db.cases.find({'name':name}) 
        return """render_template('create_success.html', case=case)"""
    return render_template('create_case.html')

@app.route('/sip')
def sip():
    transcript = mongo.db.transcripts.find({'filename':'56999975603_56999975603_12-04-2017_14-27-15.raw'})
    case = mongo.db.cases.find({'name':'iPhone 6s Screen Replacement'})
    a = transcript[0]['content']['text']
    b = case[0]['keywords']['identify']

    aa = str(b).split(" ")

    bb = str(a).split(" ")

    print set(aa).intersection(bb)
    return """hol"""

#    for t in transcript:   
#        print t['content']['text']
#    for c in case:
#        print c['keywords']['identify']
#    return render_template('1.html', transcript=transcript)
#        print result
    
@app.route('/summary')
def summary():
    return render_template('demo.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)

#to copy the ssh keys gcloud compute copy-files ~/.ssh/neem.json neemfs:~/.ssh/neem.json --zone asia-east1-a
#mongo fast commenads / mongo / use app / db.users.find()

