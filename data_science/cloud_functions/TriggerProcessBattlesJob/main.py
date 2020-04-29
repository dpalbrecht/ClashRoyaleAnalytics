from google.oauth2 import service_account
from googleapiclient.discovery import build
import googleapiclient.discovery
import datetime
from google.cloud import storage
import json
import logging
logging.getLogger().setLevel(logging.INFO)


"""
This function triggers the AI Job that makes calls to the ProcessBattles Cloud Function.

Command to deploy from cloud_functions: 
    gcloud functions deploy trigger_process_battles_job --memory=128MB --timeout=300s --source TriggerProcessBattlesJob --runtime python37 --entry-point trigger --project royaleapp --trigger-resource process_battles_gsheets --trigger-event google.pubsub.topic.publish
"""


client = storage.Client()
bucket = client.get_bucket('royale-data')
blob = bucket.get_blob('credentials/2020_04_28_trigger_process_battles_job_creds.json')
blob.download_to_filename('/tmp/creds.json')
CREDENTIALS = service_account.Credentials.from_service_account_file(
    '/tmp/creds.json', scopes=['https://www.googleapis.com/auth/cloud-platform'])


def trigger(event, context):
    process_inputs = {
        'scaleTier': 'BASIC',
        'masterConfig': {'imageUri': 'gcr.io/royaleapp/process_battles_job'},
        'pythonModule': 'main.py',
        'region': 'us-west2'
    }
    job_spec = {
        'jobId': 'process_battles_job_{}'.format(datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')), 
        'trainingInput': process_inputs
    }
    cloudml = googleapiclient.discovery.build('ml', 'v1', credentials=CREDENTIALS)
    request = cloudml.projects().jobs().create(body=job_spec, parent='projects/royaleapp')
    response = request.execute()
    logging.info(json.dumps({'status':'success', 'response_object':response}))
    return json.dumps({'status':'success', 'response_object':response}), 200