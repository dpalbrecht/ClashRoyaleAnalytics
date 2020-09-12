from google.cloud import storage
import numpy as np
import json
import pickle


"""
Make recommendations based on 100K GC data.

Command to deploy from cloud_functions: 
    gcloud functions deploy gc100krecs --memory=@GB --timeout=300s --source GC100KRecs--runtime python37 --trigger-http --entry-point get_recs --project royaleapp
"""

def get_recs(request):
	inputs = request.get_json()
	input_deck = inputs['input_deck'].split(',')
	n_recs = int(inputs['n_recs'])
	# TODO: Put error handling here for decks with fewer than 8 cards. Also for not passing n_recs
	