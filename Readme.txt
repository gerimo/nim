#1.To create a service account and have your application use it for API
#    access, run:
#        $ gcloud iam service-accounts create my-account
#        $ gcloud iam service-accounts keys create key.json
#          --iam-account=my-account@my-project.iam.gserviceaccount.com
#        $ export GOOGLE_APPLICATION_CREDENTIALS="/home/gr/.ssh/neem.json"
#        $ ./my_application.sh
#    To temporarily use your own user credentials, run:
#2. Install Google Cloud SDK / curl https://sdk.cloud.google.com | bash / exec -l $SHELL / gcloud init
#3. in production install the following python google cloud version: pip install --upgrade google-cloud==0.24.0 --user
#5. pip install gcloud pytho library $ pip install --upgrade google-api-python-client
#4  pip install --upgrade google-cloud-speech or pip install --upgrade google-cloud-speech==0.25.0 --user
#6. gcloud beta auth application-default login or gcloud auth application-default login / gcloud components update
#7. Generate an app.yaml config file https://cloud.google.com/appengine/docs/standard/python/tools/using-local-server#Python_Running_the_development_web_server
# to connect to the instance $ gcloud compute ssh neemfs
# to initiate in productive $ sudo reboot / sudo service apache2 stop / sudo python app.py &
# to connect to gcloud and run gsutil: sudo gcloud auth login

Opcion 1
# for google cloud storage
#set the google storage bucket to be accesible $ gsutil defacl set public-read gs://neemfs
#remember to include the path to your project key inside the on the <gs_service_key_file> field inside the .boto file
# pip install --upgrade google-cloud-storage --user
# $ gcloud auth application-default login
# this is the route for default credentials /home/gr/.config/gcloud/application_default_credentials.json (in case you haven't load neem.json)
# set the project name on your local other wise it won't work: $export GCLOUD_PROJECT=neem-js
# https://cloud.google.com/appengine/docs/standard/python/googlecloudstorageclient/setting-up-cloud-storage
# Please note that Google Storage Python API is depicated: http://stackoverflow.com/questions/26083985/upload-files-to-google-cloud-storage-with-google-app-engine-python?rq=1 
#from google.cloud import storage
#import gcs_oauth2_boto_plugin
#import boto
#import shutil
#import StringIO
#import tempfile
#./google-cloud-sdk/.install
#./google-cloud-sdk/bin/gcloud init
# gcloud auth login
#!/usr/bin/python
#for google storage
#from gcs_oauth2_boto_plugin.oauth2_helper import SetFallbackClientIdAndSecret
#CLIENT_ID = '455316581334-irn49vs4uscp0tj4q7pb80dc79i11o4k.apps.googleusercontent.com'
#CLIENT_SECRET = 'rs7wVFzTSFbgmuM0ZFMjdWh5'
#OAUTH2_CLIENT_ID = '455316581334-irn49vs4uscp0tj4q7pb80dc79i11o4k.apps.googleusercontent.com'
#OAUTH2_CLIENT_SECRET = 'rs7wVFzTSFbgmuM0ZFMjdWh5'
#gcs_oauth2_boto_plugin.SetFallbackClientIdAndSecret(CLIENT_ID, CLIENT_SECRET)
# URI scheme for Cloud Storage.
#GOOGLE_STORAGE = 'gs'
## URI scheme for accessing local files.
#LOCAL_FILE = 'file'

@app.route('/up', methods=['GET', 'POST'])
def up():
    UPLOAD_FOLDER = 'gs://neemfs/' 
    ALLOWED_EXTENSIONS = set(['raw','flac','mp3','wav'])
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        # upload a new file to the view
    if request.method == 'POST':
        filex = request.files['file']
        storage_client = storage.Client('neem-fs') #you can access your storage client name on the .json project key
        bucket_name = 'neemfs' #you can access on your google cloud storage profile
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(request.files['file'])
        blob.upload_from_filename(str(filex.filename))
    return render_template('tester.html')

Opcion 2 
# for google cloud storage client library or gcs
# https://cloud.google.com/appengine/docs/standard/python/tools/using-local-server
# Install Google AppEngine Cloud Storage Client Library (It's a library, NOT part of the API) - pip install GoogleAppEngineCloudStorageClient --user
# Run dev_appserver.py with the flag --default_gcs_bucket_name [BUCKET_NAME], replacing [BUCKET_NAME] with the name of the Cloud Storage bucket you are using.
#This flag controls the bucket that will be returned when your application calls file.DefaultBucketName(ctx).
# just in case install the following: gcloud components install app-engine-python / gcloud components install app-engine-python-extras
import logging
import os
import cloudstorage as gcs
import webapp2
from google.appengine.api import app_identity
# dev_appserver.py ~/Escritorio/ --default_gcs_bucket_name neem-fs.appspot.com
