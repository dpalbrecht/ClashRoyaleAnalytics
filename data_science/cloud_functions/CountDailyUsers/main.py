from google.cloud import storage
import datetime
import pandas as pd
from io import BytesIO
import os


"""
This function counts the number of users in user_data.

Command to deploy from cloud_functions: 
    gcloud functions deploy count_daily_users --memory=128MB --timeout=300s --source CountDailyUsers --runtime python37 --entry-point count --project royaleapp --trigger-resource daily_user_count --trigger-event google.pubsub.topic.publish
"""


def count(event, context):
    # Count users
    client = storage.Client()
    bucket = client.get_bucket('royale-data')
    blobs = bucket.list_blobs(prefix='user_data/')
    blob_names = [b.name for b in blobs]
    num_users = len(blob_names) - 1
    date = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime('%m/%d/%Y')

    # Add to existing data
    df = pd.read_csv(BytesIO(bucket.get_blob('data/daily_user_count.csv').download_as_string()))
    df = df.append(pd.DataFrame({'date':[date], 'count':[num_users]}))
    df = df.groupby('date', as_index=False).first()
    
    # Save to storage
    fname = 'daily_user_count.csv'
    local_fname = '/tmp/'+fname
    df.to_csv(local_fname, index=False)
    bucket.blob('data/{}'.format(fname)).upload_from_file(open(local_fname, 'rb'))
    os.remove(local_fname)