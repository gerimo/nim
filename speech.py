import sys
reload(sys)
# play -r 8000 -b 16 -c 1 -e signed [226612700]_[226612700]_[30-03-2017]_[16-48-00].raw

sys.setdefaultencoding('utf-8')
import time
import io
import os

# Imports the Google Cloud client library
from google.cloud import speech
hints = ['pantalla', 'iphone', '119', '69','bateria']
client = speech.Client()
sample = client.sample(source_uri='gs://neemfs/[+56998417174]_[+56998417174]_[31-03-2017]_[12-41-34].raw',
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