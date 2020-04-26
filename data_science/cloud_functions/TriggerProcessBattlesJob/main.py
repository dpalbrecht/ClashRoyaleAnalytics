from google.oauth2 import service_account
from googleapiclient.discovery import build
import googleapiclient.discovery
import datetime
from google.cloud import storage
import json


"""
This function triggers the AI Job that makes calls to the ProcessBattles Cloud Function.

Command to deploy from cloud_functions: 
    gcloud functions deploy trigger_process_battles_job --memory=128MB --timeout=300s --source TriggerProcessBattlesJob --runtime python37 --entry-point trigger --project RoyaleApp --trigger-resource process_battles_gsheets --trigger-event google.pubsub.topic.publish
"""


client = storage.Client()
bucket = client.get_bucket('royale-data')
blob = bucket.get_blob('credentials/{}'.format(creds_fname)) ## TODO: get credentials and replace creds_fname with the name of the saved file
blob.download_to_filename('/tmp/creds.json')
CREDENTIALS = service_account.Credentials.from_service_account_file(
    '/tmp/creds.json', scopes=['https://www.googleapis.com/auth/cloud-platform'])


def trigger(request):
    process_inputs = {
        'scaleTier': 'BASIC',
        'masterConfig': {'imageUri': 'gcr.io/royaleapp/{}'.format(image_uri_name)}, #  ## TODO: build and tag image for AI Job. Place name here instead of image_uri_name
        'pythonModule': 'main.py',
        'region': 'us-west2'
    }
    job_spec = {
        'jobId': 'process_battles_{}'.format(datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')), 
        'trainingInput': process_inputs
    }
    cloudml = googleapiclient.discovery.build('ml', 'v1', credentials=CREDENTIALS)
    request = cloudml.projects().jobs().create(body=job_spec, parent='projects/royaleapp')
    response = request.execute()
    return json.dumps({'status':'success', 'response_object':response}), 200