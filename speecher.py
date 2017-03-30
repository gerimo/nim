from google.cloud import speech
client = speech.Client()
sample = client.sample(source_uri='~/Escritorio/flask/uploads/speech.flac',
                        encoding=speech.Encoding.FLAC)
results = sample.sync_recognize(speech.Encoding.FLAC, 16000, source_uri='~/Escritorio/flask/uploads/speech.flac', language_code='en-GB',max_alternatives=2)
for result in results:
     for alternative in result.alternatives:
         print('=' * 20)
         print('transcript: ' + alternative.transcript)
         print('confidence: ' + alternative.confidence)


