import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import io
import os
from flask.ext.pymongo import PyMongo
mongo = PyMongo(app)

# Imports the Google Cloud client library
from google.cloud import speech

# Instantiates a client
speech_client = speech.Client()

# The name of the audio file to transcribe
file_name = os.path.join(
    os.path.dirname(__file__),
    'speech',
    'speech.flac')

# Loads the audio into memory
with io.open(file_name, 'rb') as audio_file:
    content = audio_file.read()
    audio_sample = speech_client.sample(
        content,
        source_uri=None,
        encoding='FLAC')

# Detects speech in the audio file
alternatives = speech_client.speech_api.sync_recognize(audio_sample,language_code='es-CL')

for alternative in alternatives:
    print('Transcript: {}'.format(alternative.transcript))