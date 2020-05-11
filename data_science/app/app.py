from flask import Flask, render_template, request, jsonify, abort
import requests
import pandas as pd
import numpy as np
from google.cloud import storage
import pickle
import os
import itertools
from collections import Counter
import datetime
from statsmodels.stats.proportion import proportion_confint

app = Flask(__name__)


@app.before_first_request
def load_vars():
    global TOKEN, CLIENT, BUCKET, HEADER
    TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImQ1ZWI1Nzk0LThjZjgtNDVlNi05ZGFjLWIzYmU5ZTBkMTVjOSIsImlhdCI6MTU4NTg3NDg3MSwic3ViIjoiZGV2ZWxvcGVyLzE4OGM5NTY0LWFhYjgtZWYzNS02ZTdiLTcwZWJmZWNmMzBhNCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI3Ni4xNzYuMjkuNzUiXSwidHlwZSI6ImNsaWVudCJ9XX0.mJ4gkJKHYKEbs95og1DM3OybAieXjC5ypC2dVh0IQYRviu3R9FJmyZTwC3YB0yrjvpg8NpCsZDvUDtrcwEz_IQ"
    HEADER = {"Authorization": "Bearer {}".format(TOKEN)}
    try:
        CLIENT = storage.Client()
    except:
        CLIENT = storage.Client.from_service_account_json('../royaleapp-296a6cea39ad.json')
    BUCKET = CLIENT.bucket('royale-data')


def get_battles(player_tag):
    # Clean input tag
    player_error_flag = False
    if player_tag.startswith('#'):
        player_tag = player_tag[1:]

    # Get battle profile and check for errors
    profile_response = requests.get('https://api.clashroyale.com/v1/players/%23{}'.format(player_tag),
        headers=HEADER)
    profile_response = eval(profile_response.text.replace('false', 'False').replace('true', 'True').replace('null','None'))
    if profile_response.get('tag') is None:
        player_error_flag = True

    # Get battle logs
    battles_response = requests.get('https://api.clashroyale.com/v1/players/%23{}/battlelog'.format(player_tag),
        headers=HEADER)
    battles_response = eval(battles_response.text.replace('false', 'False').replace('true', 'True'))

    return player_error_flag, profile_response, battles_response

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

def process_battles(player_tag, battle_list):
    # read in data from storage
    # if no data, create data
    if player_tag.startswith('#'):
        player_tag = player_tag[1:]
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
    # handle errors by skipping battles
    for battle in battle_list[::-1]:
        # make sure you don't add the same battles twice
        # battles in 2v2, where it's harder to get data for both teams, are excluded
        battle_times = data['battle_time']
        try:
            if (battle['battleTime'] not in battle_times) and ('2v2' not in battle['type']):
                if battle['team'][0]['crowns'] > battle['opponent'][0]['crowns']:
                    win_loss = 'win'
                elif battle['team'][0]['crowns'] < battle['opponent'][0]['crowns']:
                    win_loss = 'loss'
                else:
                    assert 1 == 2

                # if the battle is a tournament, take the last available trophy count
                if battle['type'] == 'tournament':
                    if len(data['team_trophy_count']) > 0:
                        team_trophy_count = data['team_trophy_count'][-1]
                    else:
                        team_trophy_count = battle['team'][0]['startingTrophies']
                    if team_trophy_count is None:
                        team_trophy_count = 0
                else:
                    team_trophy_count = battle['team'][0]['startingTrophies']

                battle_time = battle['battleTime']
                team_cards = [card['name'] for card in battle['team'][0]['cards']]
                opponent_cards = [card['name'] for card in battle['opponent'][0]['cards']]
                game_mode = clean_game_mode("{} - {}".format(battle['type'], battle['gameMode']['name']))
                arena = battle['arena']['name']

                data['win_loss'].append(win_loss)
                data['team_trophy_count'].append(team_trophy_count)
                data['battle_time'].append(battle_time)
                data['team_cards'].append(team_cards)
                data['opponent_cards'].append(opponent_cards)
                data['game_mode'].append(game_mode)
                data['arena'].append(arena)
        except:
            continue

    # save to storage
    local_fname = '{}.p'.format(player_tag)
    with open(local_fname, 'wb') as f:
        pickle.dump(data, f)
    BUCKET.blob('user_data/{}.p'.format(player_tag)).upload_from_file(open(local_fname, 'rb'))
    os.remove(local_fname)

    # Get all available team cards
    your_team_cards = sorted(set(itertools.chain(*data['team_cards'])))
    # Get all available opponent cards
    opponent_team_cards = sorted(set(itertools.chain(*data['opponent_cards'])))
    # Get all available game modes
    game_modes = sorted(set(data['game_mode']))
    # Get all available arenas
    arenas = sorted(set(data['arena']))
    # Get min and max trophies
    trophy_dict = {'min':str(min(data['team_trophy_count'])),
                   'max':str(max(data['team_trophy_count']))}

    return data, your_team_cards, opponent_team_cards, game_modes, arenas, trophy_dict

def process_data(data, filter_dict):
    win_card_stats = {}
    messages = []
    battle_times = pd.to_datetime(np.array(data['battle_time']))
    team_cards = np.array(data['team_cards'])
    opponent_cards = np.array(data['opponent_cards'])
    team_trophy_count = np.array(data['team_trophy_count'])
    game_mode = pd.Series(np.array(data['game_mode']))
    arena = pd.Series(np.array(data['arena']))
    win_loss = np.array(data['win_loss'])

    # Find battles that were won
    win_inds = np.where(win_loss=='win')[0]

    # Find battles between battle times
    if filter_dict['battle_time_range'] == []:
        time_inds = np.array(range(len(battle_times)))
    else:
        end = datetime.datetime.now(datetime.timezone.utc)
        if filter_dict['battle_time_range'] == 'Last Day':
            num_days = 1
        elif filter_dict['battle_time_range'] == 'Last Week':
            num_days = 7
        else:
            num_days = 30
        start = end - datetime.timedelta(days=num_days)
        time_inds = np.where((battle_times>=start) & (battle_times<=end))[0]
    if len(time_inds) == 0:
        messages.append('You have not played games within this time frame.')

    # Find battles that match game modes
    if filter_dict['game_modes'] == []:
        game_mode_inds = np.array(range(len(game_mode)))
    else:
        game_mode_inds = np.array(game_mode[game_mode.isin(filter_dict['game_modes'])].index)

    # Find battles that match arena
    if filter_dict['arena'] == []:
        arena_inds = np.array(range(len(arena)))
    else:
        arena_inds = np.array(arena[arena.isin(filter_dict['arena'])].index)

    # Find battles within a given trophy range
    if (filter_dict['team_trophy_count_range'] == []):
        trophy_inds = np.array(range(len(team_trophy_count)))
    else:
        trophy_inds = np.where((team_trophy_count>=filter_dict['team_trophy_count_range'][0]) \
                               & (team_trophy_count<=filter_dict['team_trophy_count_range'][-1]))[0]

    # Find battles with team decks containing specific cards
    if filter_dict['team_cards'] == []:
        team_card_inds = np.array(range(len(team_cards)))
    else:
        team_card_inds = np.array([n for n, cards in enumerate(team_cards) \
                                   if len(set(filter_dict['team_cards']).intersection(set(cards))) == len(filter_dict['team_cards'])])
    if len(team_card_inds) == 0:
        messages.append('You have not played with this combination of cards.')

    # Find battles with opponent decks containing any cards
    if filter_dict['opponent_cards'] == []:
        opponent_card_inds = np.array(range(len(opponent_cards)))
    else:
        opponent_card_inds = np.array([n for n, cards in enumerate(opponent_cards) \
                                       if len(set(filter_dict['opponent_cards']).intersection(set(cards))) == len(filter_dict['opponent_cards'])])
    if len(opponent_card_inds) == 0:
        messages.append('You have not played any opponents with this combination of cards.')

    # Find intersection of all filters except wins
    all_inds = [time_inds, game_mode_inds, arena_inds, trophy_inds, team_card_inds, opponent_card_inds]
    shared_inds = np.array(list(set(all_inds[0]).intersection(*all_inds[1:])))

    if len(shared_inds) != 0:
        all_opponent_cards_dict = dict(Counter(itertools.chain(*opponent_cards[shared_inds])))
        all_inds.append(win_inds)
        win_shared_inds = np.array(list(set(all_inds[0]).intersection(*all_inds[1:])))
        total_win_rate = np.round(len(win_shared_inds)/len(shared_inds)*100, 2)
        if len(win_shared_inds) != 0:
            win_opponent_cards_dict = dict(Counter(itertools.chain(*opponent_cards[win_shared_inds])))
        else:
            win_opponent_cards_dict = {}
        for card, count in all_opponent_cards_dict.items():
            if win_opponent_cards_dict.get(card) is None:
                win_card_stats[card] = 0
            else:
                win_card_stats[card]= win_opponent_cards_dict.get(card)/count
    else:
        all_opponent_cards_dict = {}
        total_win_rate = 0
        messages.append('This combination of filters does not produce results.')

    if data == {
        'battle_time':[],
        'team_cards':[],
        'opponent_cards':[],
        'team_trophy_count':[],
        'game_mode':[],
        'arena':[],
        'win_loss':[]
    }:
        messages = ['You don\'t have any 1v1 battles to analyze right now. Play some battles and try again!']

    return win_card_stats, all_opponent_cards_dict, messages, len(shared_inds), total_win_rate


@app.route('/')
def index():
    return render_template('index.html')

def rank_results(cards, play_counts, win_percents):
    if len(cards) > 0:
        int_play_counts = np.array(play_counts).astype(int)
        float_win_percs = np.array(win_percents).astype(int)/100
        # ranking = np.argsort((int_play_counts/max(int_play_counts)) * float_win_percs)[::-1]
        confidence_numbers = proportion_confint(np.round(float_win_percs*int_play_counts).astype(int),int_play_counts, alpha=0.05, method='wilson')[0]
        # confidence_numbers = proportion_confint(float_win_percs*int_play_counts,int_play_counts, alpha=0.05, method='wilson')[0]
        ranking = np.argsort(confidence_numbers)[::-1]
        ranked_cards = np.array(cards)[ranking].tolist()
        ranked_play_counts = np.array(play_counts)[ranking].tolist()
        ranked_win_percs = np.array(win_percents)[ranking].tolist()
        return ranked_cards, ranked_play_counts, ranked_win_percs
    else:
        return cards, play_counts, win_percents

def process_and_return_data(filter_dict=None):
    if filter_dict is None:
        filter_dict = {
            'team_cards':[],
            'opponent_cards':[],
            'team_trophy_count_range':[],
            'battle_time_range':[],
            'game_modes':[],
            'arena':[]
        }
    processed_win_stats, all_opponent_card_plays, messages, num_battles, total_win_rate = process_data(PROCESSED_BATTLES, filter_dict)
    cards = []
    win_percents = []
    play_counts = []
    for card, play_count in all_opponent_card_plays.items():
        cards.append(card)
        play_counts.append(str(int(play_count)))
        win_percents.append(str(int(processed_win_stats[card]*100)))

    cards, play_counts, win_percents = rank_results(cards, play_counts, win_percents)

    return cards, play_counts, win_percents, messages, num_battles, total_win_rate

@app.route('/process', methods=['POST'])
def process_front_page():
    content = request.get_json()
    player_tag = content.get('player_tag')

    player_error_flag, player_profile, battles = get_battles(player_tag)

    if player_error_flag:
        return jsonify(player_error_flag=player_error_flag)
    else:
        global PROCESSED_BATTLES
        PROCESSED_BATTLES, your_team_cards, opponent_team_cards, game_modes, arenas, trophy_dict = process_battles(player_tag, battles)

        cards, play_counts, win_percents, messages, num_battles, total_win_rate = process_and_return_data()

        return jsonify(cards=cards,
                       play_counts=play_counts,
                       win_percents=win_percents,
                       messages=messages,
                       your_team_cards=your_team_cards,
                       opponent_team_cards=opponent_team_cards,
                       game_modes=game_modes,
                       arenas=arenas,
                       min_trophy=trophy_dict['min'],
                       max_trophy=trophy_dict['max'],
                       num_battles=num_battles,
                       total_win_rate=total_win_rate)

def clean_trophy_filter(raw_filter_values):
    split_vals = raw_filter_values.split(';')
    return int(split_vals[0]), int(split_vals[1])

def clean_battle_time_filter(raw_filter_list):
    if len(raw_filter_list) == 0:
        return raw_filter_list
    else:
        return raw_filter_list[0]

@app.route('/filter', methods=['POST'])
def process_filter():
    content = request.get_json()
    your_team_filter_values = content.get('your_team_filter')
    opponent_team_filter_values = content.get('opponent_team_filter')
    game_mode_filter_values = content.get('game_mode_filter')
    arena_filter_values = [] #content.get('arena_filter')
    battle_time_filter_values = clean_battle_time_filter(content.get('battle_time_filter'))
    min_trophy, max_trophy = clean_trophy_filter(content.get('trophy_filter'))

    filter_dict = {
        'team_cards':your_team_filter_values,
        'opponent_cards':opponent_team_filter_values,
        'team_trophy_count_range':[min_trophy, max_trophy],
        'battle_time_range':battle_time_filter_values,
        'game_modes':game_mode_filter_values,
        'arena':arena_filter_values
    }

    cards, play_counts, win_percents, messages, num_battles, total_win_rate = process_and_return_data(filter_dict)

    return jsonify(cards=cards,
                   play_counts=play_counts,
                   win_percents=win_percents,
                   messages=messages,
                   num_battles=num_battles,
                   total_win_rate=total_win_rate)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='localhost')
