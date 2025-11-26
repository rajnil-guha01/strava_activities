import requests
import time
from datetime import datetime, timedelta
import sys

def check_token_expiry(client_id: int, scope: str, catalog: str, schema: str, token_table: str) -> str:
    """
    Check and refresh Strava API access token if expired.
    Parameters:
    - client_id (int): Strava client ID (athlete ID).
    - scope (str): Scope of the token.
    - catalog (str): Database catalog name.
    - schema (str): Database schema name.
    - token_table (str): Table name where tokens are stored.
    Returns:
    - str: Valid Strava access token.
    """

    # Get token details from strava tokens table using client_id and scope
    token_table_name = f'{catalog}.{schema}.{token_table}'
    tokens_df = spark.sql(f"""select scope, access_token, expires_at, refresh_token from {token_table_name} where 
                          athlete_id = {client_id} and scope = '{scope}' """)
    # Validate if token details are found
    if tokens_df.count() == 0:
        print(f"No token details found for the given client_id: {client_id} and scope: {scope}.")
        sys.exit(1)
    
    token_details = tokens_df.collect()[0]
    strava_access_token = token_details['access_token']
    strava_scope = token_details['scope']
    strava_token_expire_time = token_details['expires_at']
    strava_refresh_token = token_details['refresh_token']
    current_unix_time = time.time()
    # Fetch client secret from databricks secrets
    strava_client_secret = dbutils.secrets.get(scope = 'strava_secrets', key = 'STRAVA_CLIENT_SECRET')

    if strava_token_expire_time and strava_token_expire_time < current_unix_time:
        # Token has expired and its time to request for a new token
        print("Strava access token has expired. Refreshing the token...")
        response_for_token = requests.post(
            "https://www.strava.com/api/v3/oauth/token",
            params = {
                "client_id": client_id,
                "client_secret": strava_client_secret,
                "grant_type": "refresh_token",
                "refresh_token": strava_refresh_token
            }
        )
        token_response = response_for_token.json()
        strava_access_token = token_response['access_token']
        strava_refresh_token = token_response['refresh_token']
        strava_token_expire_time = token_response['expires_at']
        # Update the new token details back to the tokens table
        update_query = f"""
        update {token_table_name} set access_token = '{strava_access_token}, refresh_token = '{strava_refresh_token}',
        expires_at = {strava_token_expire_time} where athlete_id = {client_id} and scope = '{scope}'
        """
        spark.sql(update_query)
        print("Strava access token refreshed and updated in the tokens table.")
    
    return strava_access_token
