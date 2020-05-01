from google.cloud import storage
import pickle
import requests
import os
import numpy as np
import logging
logging.getLogger().setLevel(logging.INFO)


"""
This function processes a given player tag and saves data to storage.

Command to deploy from cloud_functions: 
    gcloud functions deploy proccessplayerbattles --vpc-connector process-battles-vpc --egress-settings all --memory=1GB --timeout=300s --source ProcessBattles --runtime python37 --trigger-http --entry-point process_battles --project royaleapp
"""


# Globals
client = storage.Client(project='royaleapp')
BUCKET = client.bucket('royale-data')
blob = BUCKET.get_blob('credentials/2020_04_26_clash_token_static.txt')
TOKEN = blob.download_as_string().decode('utf-8')

def clean_game_mode(game_mode):
    game_mode = game_mode.replace('_', '')
    count = 0
    for n, m in enumerate(game_mode):
        try:
            test = int(m)
            int_flag = True
        except:
            int_flag = False
        if (m.isupper() or int_flag) and (n != 0):
            game_mode = game_mode[:n+count] + ' ' + game_mode[n+count:]
            count += 1
    return game_mode.title().replace('  ', ' ').replace('Pv P', 'PvP').replace('2V 2', '2V2').replace('1V 1', '1V1')

def process_battles(request):
    data = request.get_json()
    player_tag = data['player_tag']
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
    logging.info('data length before processing: {}'.format(len(data['win_loss'])))
    battle_list = eval(response.text.replace('false', 'False').replace('true', 'True'))
    for battle in battle_list:
        # make sure you don't add the same battles twice
        # battles in 2v2, where it's harder to get data for both teams, are excluded
        if (battle['battleTime'] not in data['battle_time']) and ('2v2' not in battle['type']):
            if battle['team'][0]['crowns'] > battle['opponent'][0]['crowns']:
                data['win_loss'].append('win')
            elif battle['team'][0]['crowns'] < battle['opponent'][0]['crowns']:
                data['win_loss'].append('loss')
            else:
                logging.info('Player tag {} had a battle at {} where neither player had more crowns.'.format(player_tag, battle['battleTime']))
                continue
            data['battle_time'].append(battle['battleTime'])
            data['team_cards'].append([card['name'] for card in battle['team'][0]['cards']])
            data['opponent_cards'].append([card['name'] for card in battle['opponent'][0]['cards']])
            data['team_trophy_count'].append(battle['team'][0]['startingTrophies'])
            data['game_mode'].append(clean_game_mode("{} - {}".format(battle['type'], battle['gameMode']['name'])))
            data['arena'].append(battle['arena']['name'])
    logging.info('data length after processing: {}'.format(len(data['win_loss'])))
    # save to storage
    local_fname = '/tmp/{}.p'.format(player_tag)
    with open(local_fname, 'wb') as f:
        pickle.dump(data, f)
    BUCKET.blob('user_data/{}.p'.format(player_tag)).upload_from_file(open(local_fname, 'rb'))
    os.remove(local_fname)