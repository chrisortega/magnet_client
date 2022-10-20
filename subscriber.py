from ast import Try
import os
from typing import Any
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
import requests
from uuid import uuid4
import json
import sys
import asyncio

from magnet2torrent import Magnet2Torrent, FailedToFetchException

credentials_path = 'neon-mote-358900-516d336a19dd.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path


timeout = 5.0                                                                       # timeout in seconds

subscriber = pubsub_v1.SubscriberClient()
subscription_path = 'projects/neon-mote-358900/subscriptions/magnetos-sub'



def fetch_that_torrent(magnet):
    m2t = Magnet2Torrent(magnet)
    try:
        filename, torrent_data =  m2t.retrieve_torrent()
        return filename, torrent_data
    except FailedToFetchException:
        print("Failed")
        return False,None

def save_magnets_to_dir(magnet):
    try:
        URL = magnet
        response = requests.get(URL)    
        open(f"{uuid4()}.torrent", "wb").write(response.content)
        return True
    except Exception as e:
        print(f"{e}")
        return False



def callback(message):
    

    magnet = json.loads(message.data)
    if "magnet" in magnet['url']:
        filename,data =  fetch_that_torrent(magnet['url'])
        save_magnets_to_dir(magnet = filename)
        print("this is a magnet")

    else:
        save_magnets_to_dir(magnet = magnet['url'])
        print("saved")


    message.ack()           




if __name__ == "__main__":
    
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f'Listening for messages on {subscription_path}')    
    with subscriber:                                                # wrap subscriber in a 'with' block to automatically call close() when done
        try:
            # streaming_pull_future.result(timeout=timeout)
            streaming_pull_future.result()                          # going without a timeout will wait & block indefinitely
        except TimeoutError:
            streaming_pull_future.cancel()                          # trigger the shutdown
            streaming_pull_future.result()                          # block until the shutdown is complete



