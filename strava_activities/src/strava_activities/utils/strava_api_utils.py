from pyspark.sql import SparkSession
import requests
import time
from datetime import datetime, timedelta
import sys
import os

def check_token_expiry(spark: SparkSession, client_id: str, scope: str, catalog: str, schema: str, token_table: str, secure_path: str) -> str:
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

    # strava_client_secret = dbutils.secrets.get(scope = secret_scope, key = 'STRAVA_CLIENT_SECRET')
    # strava_client_secret = os.environ.get('STRAVA_CLIENT_SECRET')
    with open(secure_path, "r") as f:
        strava_client_secret = f.read().strip()

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
        update {token_table_name} set access_token = '{strava_access_token}', refresh_token = '{strava_refresh_token}',
        expires_at = {strava_token_expire_time} where athlete_id = '{client_id}' and scope = '{scope}'
        """
        spark.sql(update_query)
        print("Strava access token refreshed and updated in the tokens table.")
    
    return strava_access_token

def get_athlete_profile_details(spark: SparkSession, client_id: str, scope: str, catalog: str, schema: str, token_table: str, secure_path: str) -> dict:
    """
    Get athlete profile details from Strava API.
    Parameters:
    - client_id (int): Strava client ID (athlete ID).
    - scope (str): Scope of the token.
    - catalog (str): Database catalog name.
    - schema (str): Database schema name.
    - token_table (str): Table name where tokens are stored.
    Returns:
    - dict: Athlete profile details from Strava API.
    """
    # Fetch valid access token
    strava_access_token = check_token_expiry(spark = spark, client_id = client_id, scope = scope, catalog = catalog, 
                                             schema = schema, token_table = token_table, secure_path = secure_path)
    print("Getting athlete profile details from Strava API...")
    response = requests.get(
        "https://www.strava.com/api/v3/athlete",
        headers = {"Authorization": f"Bearer {strava_access_token}"}
    )
    print("Athlete profile details fetched successfully.")
    return response
