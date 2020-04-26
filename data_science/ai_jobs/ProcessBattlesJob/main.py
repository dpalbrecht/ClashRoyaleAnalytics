from google.cloud import storage
import aiohttp
import asyncio
import nest_asyncio
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import logging
logging.getLogger().setLevel(logging.INFO)

COUNT = 0

def read_player_tags():
    client = storage.Client()
    bucket = client.bucket('royale-data')
    blob = bucket.get_blob('credentials/2020_04_23_gsheet_credentials.json')
    creds_fname = '/tmp/creds.json'
    blob.download_to_filename(creds_fname)
    credentials = Credentials.from_service_account_file(creds_fname, scopes=['https://spreadsheets.google.com/feeds'])
    os.remove(creds_fname)
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId='1cmSIq5-6NI5Bn1n8WTfaVTYthxTIRUQ8aNsDTixsHno',
                                range='Sheet1').execute()
    return [tag for tag in result['values']]

async def call_process_battles(player_tags):
    connector = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=connector) as session:
        post_tasks = [do_post(session, player_tag) for player_tag in player_tags]      
        await asyncio.gather(*post_tasks)
        
async def do_post(session, tag):
    try:
        async with session.post("", # TODO: Place HTTP trigger for cloud function here 
                                json={'player_tag':tag}) as response:
            data = await response.text()
            logging.info("Successfully processed player tag: {}".format(tag))
            COUNT += 1
    except asyncio.TimeoutError:
        logging.info("asyncio TimeoutError on player tag: {}".format(tag))

def main():
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    player_tags = read_player_tags()
    logging.info("Beginning to process {} tags...".format(len(player_tags)))
    loop.run_until_complete(call_process_battles(player_tags))
    logging.info("Processed {} tags...".format(len(COUNT)))
    logging.info("Job complete!")


if __name__ == '__main__':
    main()