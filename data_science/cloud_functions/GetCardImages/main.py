from google.cloud import storage
import requests
import numpy as np
import logging
import json
logging.getLogger().setLevel(logging.INFO)


"""
Get card images dictionary.

Command to deploy from cloud_functions: 
    gcloud functions deploy getcardimages --vpc-connector process-battles-vpc --egress-settings all --memory=1GB --timeout=300s --source GetCardImages --runtime python37 --trigger-http --entry-point get_card_images --project royaleapp
"""


# Globals
client = storage.Client(project='royaleapp')
BUCKET = client.bucket('royale-data')
blob = BUCKET.get_blob('credentials/2020_04_26_clash_token_static.txt')
TOKEN = blob.download_as_string().decode('utf-8')


def get_card_images(request):
    response = requests.get('https://api.clashroyale.com/v1/cards', 
                        headers={"Authorization": "Bearer {}".format(TOKEN)})
    cards_response = eval(response.text.replace('false', 'False').replace('true', 'True'))
    card_dict = {r['name']:r['iconUrls']['medium'] for r in cards_response['items']}
    return json.dumps(card_dict)