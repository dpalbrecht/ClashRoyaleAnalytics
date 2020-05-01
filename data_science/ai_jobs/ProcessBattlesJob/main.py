from google.cloud import storage
import aiohttp
import asyncio
import nest_asyncio
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os
import logging
logging.getLogger().setLevel(logging.INFO)


def read_player_tags():
    client = storage.Client()
    bucket = client.bucket('royale-data')
    blobs = bucket.list_blobs(prefix='user_data')
    player_tags = [blob.name.split('/')[1][:-2] for blob in blobs if blob.name.endswith('.p')]
    return player_tags

async def call_process_battles(player_tags):
    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        post_tasks = [do_post(session, player_tag) for player_tag in player_tags]      
        out = await asyncio.gather(*post_tasks)
        return out
        
async def do_post(session, tag):
    try:
        async with session.post("https://us-central1-royaleapp.cloudfunctions.net/proccessplayerbattles",
                                json={'player_tag':tag}) as response:
            data = await response.text()
            if data == 'OK':
                logging.info("Successfully processed player tag: {}".format(tag))
                return 1
            else:
                logging.info("Could not process player tag: {}".format(tag))
    except asyncio.TimeoutError:
        logging.info("asyncio TimeoutError on player tag: {}".format(tag))

def main():
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    player_tags = read_player_tags()
    logging.info("Beginning to process {} tags...".format(len(player_tags)))
    success_tags = loop.run_until_complete(call_process_battles(player_tags))
    logging.info("Successfully processed {} tags...".format(len(success_tags)))
    logging.info("Job complete!")


if __name__ == '__main__':
    main()