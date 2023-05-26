import os
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
import keyboard
import sys
import requests
import jwt

dir_path = os.path.dirname(os.path.realpath(__file__))

credentials_path = f'{dir_path}\key.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
server = 'http://192.168.100.100'

timeout = 5.0                                                                       # timeout in seconds

subscriber = pubsub_v1.SubscriberClient()
subscription_path = 'projects/neon-mote-358900/subscriptions/gdoor-sub'


def open_secret():
    with open('secret.txt') as f:
        lines = f.read()
        return lines

def toggle_door():
    requests.get(f"{server}/api/toggle")

def submitrequest(token):
    try:
        decoded = jwt.decode(token, key=open_secret(), algorithms=['HS256', ])
        toggle_door()
    except Exception as e:
        print(e)
    


def callback(message):
    #print(f'data: {message.data}')
    submitrequest(token=message.data)
    message.ack()           


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f'Listening for messages on {subscription_path}')


with subscriber:                                                # wrap subscriber in a 'with' block to automatically call close() when done
    try:
        # streaming_pull_future.result(timeout=timeout)
        streaming_pull_future.result()  
        if keyboard.is_pressed('Esc'):
            print("\nyou pressed Esc, so exiting...")
            sys.exit(0)                                # going without a timeout will wait & block indefinitely
    except TimeoutError:
        streaming_pull_future.cancel()                          # trigger the shutdown
        streaming_pull_future.result()
                                  # block until the shutdown is complete