from google.cloud import storage
import pickle
import requests
import os
import numpy as np
import logging
logging.getLogger().setLevel(logging.INFO)


"""
Get battles with a player tag.

Command to deploy from cloud_functions: 
    gcloud functions deploy getbattles --vpc-connector process-battles-vpc --egress-settings all --memory=1GB --timeout=300s --source GetBattles --runtime python37 --trigger-http --entry-point get_battles --project royaleapp
"""


# Globals
client = storage.Client(project='royaleapp')
BUCKET = client.bucket('royale-data')
blob = BUCKET.get_blob('credentials/2020_04_26_clash_token_static.txt')
TOKEN = blob.download_as_string().decode('utf-8')


def get_battles(request):
    data = request.get_json()
    player_tag = data['player_tag']
    response = requests.get('https://api.clashroyale.com/v1/players/%23{}/battlelog'.format(player_tag), 
                            headers={"Authorization": "Bearer {}".format(TOKEN)})
    battles_response = response.text.replace('false', 'False').replace('true', 'True').replace('null','None')
    return battles_response