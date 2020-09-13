from google.cloud import storage
import numpy as np
import json
import pickle
from sklearn.preprocessing import normalize
import operator

"""
Make recommendations based on 100K GC data.

Command to deploy from cloud_functions: 
    gcloud functions deploy gc100krecs --memory=2GB --timeout=300s --source=GC100KRecs --runtime=python37 --trigger-http --entry-point=get_recs --project=royaleapp
"""

client = storage.Client()
bucket = client.bucket('royale-data')
def read_file(fname):
    return pickle.loads(bucket.get_blob('100k_gc_deck_models/'+fname).download_as_string())

STATS_DICT = read_file('stats_dict.p')
CARD2IND = read_file('card2ind.p')
WINCON2IND = read_file('wincon2ind.p')
DECK_MATRIX = read_file('deck_matrix.p')
ONE_HOT_DECK_MATRIX = read_file('one_hot_deck_matrix.p')
ONE_HOT_WINCON_DECK_MATRIX = read_file('one_hot_wincon_deck_matrix.p')
NORMED_DECK_COUNTS = read_file('normed_deck_counts.p')
DECKS = read_file('decks.p')

def ind2deck(input_inds, input_deck):
    return [DECKS[r] for r in input_inds if DECKS[r] != input_deck]
    
def get_recs(request):
    inputs = request.get_json()
    if inputs.get('input_deck') is None:
        return json.dumps({'success':False, 'message':'You did not pass \'input_deck\' as a parameter.'})
    input_deck = inputs['input_deck'].split(',')
    if len(input_deck) < 8:
        return json.dumps({'success':False, 'message':'You passed fewer than 8 cards in your deck: {}'.format(input_deck)})
    for card in input_deck:
        if card not in CARD2IND.keys():
            return json.dumps({'success':False, 'message':'Card \'{}\' is not a valid input.'.format(card)})
    if inputs.get('n_recs') is None:
        n_recs = 5
    else:
        n_recs = int(inputs['n_recs'])
        
    # Make output dictionary
    rec_dict = {}
    
    # Make card stats embedding
    stat_embedding = normalize(np.percentile(np.array([STATS_DICT[c] for c in input_deck]), 
                                             list(np.arange(0,105,5)), axis=0).flatten().reshape(-1, 1), norm='l2', axis=0).reshape(1,-1)[0]
    
    # Make one-hot embedding
    onehot_embedding = np.zeros(99)
    for card in input_deck:
        onehot_embedding[CARD2IND[card]] = 1
    onehot_embedding = normalize(onehot_embedding.reshape(-1, 1), norm='l2', axis=0).reshape(1,-1)[0]
    
    # Make one-hot/wincon embedding
    onehot_wincon_embedding = np.zeros(99)
    for card in input_deck:
        wincon_index = WINCON2IND.get(card)
        if wincon_index:
            onehot_wincon_embedding[wincon_index] = 1
    onehot_wincon_embedding = normalize(onehot_wincon_embedding.reshape(-1, 1), norm='l2', axis=0).reshape(1,-1)[0]

    # Calculate recommendation sims and extract most similar indices
    rec_sims = stat_embedding.dot(DECK_MATRIX.T)
    onehot_rec_sims = onehot_embedding.dot(ONE_HOT_DECK_MATRIX.T)
    blended_sims = rec_sims*.5 + onehot_rec_sims*.5
    blended_wincon_rec_sims = onehot_wincon_embedding.dot(ONE_HOT_WINCON_DECK_MATRIX.T)*.5 + rec_sims*.5

    rec_inds = np.argsort(rec_sims)[::-1][:n_recs]
    onehot_rec_inds = np.argsort(onehot_rec_sims)[::-1][:n_recs]
    blended_rec_inds = np.argsort(blended_sims)[::-1][:n_recs]
    blended_wincon_rec_inds = np.argsort(blended_wincon_rec_sims)[::-1]
    blended_wincon_playcount_rec_decks = [(DECKS[ind], blended_wincon_rec_sims[ind]*0.5+NORMED_DECK_COUNTS[str(DECKS[ind])]*0.5) \
                                          for ind in blended_wincon_rec_inds[:50]] # TODO: Change back to n_recs*10
    
    # Get stats recs
    rec_dict['card_constants_recs'] = ind2deck(rec_inds, input_deck)
    
    # Get one-hot recs
    rec_dict['one_hot_recs'] = ind2deck(onehot_rec_inds, input_deck)
    
    # Get 50/50 blended recs
    rec_dict['5050_blended_recs'] = ind2deck(blended_rec_inds, input_deck)
    
    # Get 50/50 wincon blended recs
    rec_dict['5050_blended_wincon_recs'] = ind2deck(blended_wincon_rec_inds[:n_recs], input_deck) 
    
    # Get 50/50 wincon play count blended recs
    rec_dict['5050_blended_wincon_playcount_recs'] = [deck for deck, sim in \
                                                       sorted(blended_wincon_playcount_rec_decks, key=operator.itemgetter(1), reverse=True)[:n_recs] \
                                                       if deck != input_deck]

    return json.dumps({'success':True, 'recs':rec_dict})