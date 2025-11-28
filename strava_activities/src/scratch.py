import requests
import os
from datetime import datetime, timedelta
import time
from pathlib import Path

def strava_api_examples():

    # check if current time exceeds the last token expiration time
    response_for_token = None
    strava_client_id = str(os.environ.get('STRAVA_CLIENT_ID'))
    strava_client_secret = os.environ.get('STRAVA_CLIENT_SECRET')
    strava_refresh_token = os.environ.get('STRAVA_REFRESH_TOKEN')
    strava_token_expire_time = int(os.environ.get('STRAVA_TOKEN_EXPIRE_TIME'))
    current_unix_time = time.time()
    print(f"Current Unix Time: {current_unix_time}")
    print(f"Strava Token Expire Time: {strava_token_expire_time}")
    print(f'strava_client_id : {strava_client_id}')
    print(f'strava_client_secret : {strava_client_secret}')
    print(f'strava_token_expire_time : {strava_token_expire_time}')
    print(f'strava_client_id : {strava_client_id}')

    # check if current time exceeds the last token expiration time
    if strava_token_expire_time and strava_token_expire_time < current_unix_time:
    # if strava_token_expire_time:
        # Token has expired and its time to request for a new token
        print("Strava access token has expired. Refreshing the token...")
        response_for_token = requests.post(
            "https://www.strava.com/api/v3/oauth/token",
            params = {
                "client_id": strava_client_id,
                "client_secret": strava_client_secret,
                "grant_type": "refresh_token",
                "refresh_token": strava_refresh_token
            }
        )
    print(response_for_token.json())
    print(type(response_for_token.json()))
    token_response = response_for_token.json()
    strava_access_token = token_response['access_token']
    response = requests.get(
        "https://www.strava.com/api/v3/athlete",
        headers = {"Authorization": f"Bearer {strava_access_token}"}
    )
    print(response.json())

def path_test():
    print(Path('..').resolve())

if __name__ == '__main__':
    path_test()