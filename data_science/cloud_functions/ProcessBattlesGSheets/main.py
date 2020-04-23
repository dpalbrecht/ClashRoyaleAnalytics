from google.cloud import storage
import pickle
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

"""
Command to deploy from cloud_functions: 
    gcloud functions deploy proccessplayerbattlesgsheets --memory=1GB --timeout=300s --source ProcessBattlesGSheets --runtime python37 --entry-point main --project RoyaleApp --trigger-resource process_battles_gsheets --trigger-event google.pubsub.topic.publish

"""

# Globals
# TODO: Need to set up cloud function with static IP? Can this happen? Need token that will work with this
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImQ1ZWI1Nzk0LThjZjgtNDVlNi05ZGFjLWIzYmU5ZTBkMTVjOSIsImlhdCI6MTU4NTg3NDg3MSwic3ViIjoiZGV2ZWxvcGVyLzE4OGM5NTY0LWFhYjgtZWYzNS02ZTdiLTcwZWJmZWNmMzBhNCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI3Ni4xNzYuMjkuNzUiXSwidHlwZSI6ImNsaWVudCJ9XX0.mJ4gkJKHYKEbs95og1DM3OybAieXjC5ypC2dVh0IQYRviu3R9FJmyZTwC3YB0yrjvpg8NpCsZDvUDtrcwEz_IQ"
CLIENT = storage.Client()
BUCKET = CLIENT.bucket('royale-data')

def read_player_tags():
    blob = BUCKET.get_blob('credentials/2020_04_23_gsheet_credentials.json')
    blob.download_to_filename('creds.json')
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = Credentials.from_service_account_file('creds.json', scopes=scope)
    os.remove('creds.json')
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId='1cmSIq5-6NI5Bn1n8WTfaVTYthxTIRUQ8aNsDTixsHno',
                                range='Sheet1').execute()
    return result

def process_battles(player_tag):
    # read in data from storage
    # if no data, create data
    blob = BUCKET.get_blob('user_data/{}.p'.format(player_tag))
    if blob is None:
        data = {
            'battle_time':[],
            'team_cards':[],
            'opponent_cards':[],
            'team_trophy_count':[],
            'game_mode':[],
            'arena':[],
            'win_loss':[]
        }
    else:
        data = pickle.loads(blob.download_as_string())
    # process battles and add to data
    response = requests.get('https://api.clashroyale.com/v1/players/%23{}/battlelog'.format(player_tag),
                            headers={"Authorization": "Bearer {}".format(TOKEN)})
    battle_list = eval(response.text.replace('false', 'False').replace('true', 'True'))
    for battle in battle_list:
        # make sure you don't add the same battles twice
        # battles in 2v2, where it's harder to get data for both teams, are excluded
        if (battle['battleTime'] not in data['battle_time']) and ('2v2' not in battle['type']):
            data['battle_time'].append(battle['battleTime'])
            data['team_cards'].append([card['name'] for card in battle['team'][0]['cards']])
            data['opponent_cards'].append([card['name'] for card in battle['opponent'][0]['cards']])
            data['team_trophy_count'].append(battle['team'][0]['startingTrophies'])
            data['game_mode'].append("{} - {}".format(battle['type'], battle['gameMode']['name']))
            data['arena'].append(battle['arena']['name'])
            if battle['team'][0]['crowns'] > battle['opponent'][0]['crowns']:
                data['win_loss'].append('win')
            elif battle['team'][0]['crowns'] < battle['opponent'][0]['crowns']:
                data['win_loss'].append('loss')
            else:
                assert 1 == 2
    # save to storage
    local_fname = '{}.p'.format(player_tag)
    with open(local_fname, 'wb') as f:
        pickle.dump(data, f)
    BUCKET.blob('user_data/{}.p'.format(player_tag)).upload_from_file(open(local_fname, 'rb'))
    os.remove(local_fname)
    
def main(request):
    result = read_player_tags()
    for val in result['values']:
        player_tag = val[0]
        process_battles(player_tag)    