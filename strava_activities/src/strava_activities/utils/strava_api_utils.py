from pyspark.sql import SparkSession
from pyspark.sql.functions import *
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

def get_strava_activities(spark: SparkSession, client_id: str, scope: str, catalog: str, schema: str, token_table: str, before_date_unix: int, after_date_unix: int, secure_path: str, load_type: str) -> dict:
    """
    Get Strava activities from Strava API for the past week from the given run_time.
    Parameters:
    - client_id (int): Strava client ID (athlete ID).
    - scope (str): Scope of the token.
    - catalog (str): Database catalog name.
    - schema (str): Database schema name.
    - token_table (str): Table name where tokens are stored.
    - run_time (str): Job run time. Format: YYYY-MM-DDTHH:MM:SS
    - secure_path (str): Path to secure file containing client secret.
    Returns:
    - dict: Strava activities from Strava API.
    """
    # before_date_unix = int(datetime.strptime(run_time, "%Y-%m-%dT%H:%M:%S").timestamp())
    # after_date = datetime.strptime(run_time, "%Y-%m-%dT%H:%M:%S") - timedelta(days=7)
    # after_date_unix = int(after_date.timestamp())

    # Fetch valid access token
    strava_access_token = check_token_expiry(spark = spark, client_id = client_id, scope = scope, catalog = catalog, 
                                             schema = schema, token_table = token_table, secure_path = secure_path)
    print("Getting Strava activities from Strava API...")
    if load_type == 'I':
        response = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers = {"Authorization": f"Bearer {strava_access_token}"},
            params = {
                "before": before_date_unix,
                "after": after_date_unix
            }
        )
    else:
        response = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers = {"Authorization": f"Bearer {strava_access_token}"},
            params = {
                "before": before_date_unix,
                "after": after_date_unix,
                "per_page": 100
            }
        )
    print(f"Strava activities fetched successfully for activities between {after_date_unix} and {before_date_unix}")
    return response

def get_all_strava_activities(spark: SparkSession, client_id: str, scope: str, catalog: str, schema: str, token_table: str, secure_path: str) -> list:
    """
    Get all Strava activities from Strava API.
    Parameters:
    - client_id (int): Strava client ID (athlete ID).
    - scope (str): Scope of the token.
    - catalog (str): Database catalog name.
    - schema (str): Database schema name.
    - token_table (str): Table name where tokens are stored.
    - secure_path (str): Path to secure file containing client secret.
    Returns:
    - list: All Strava activities from Strava API.
    """
    after_date = datetime.strptime("2024-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
    after_date_unix = int(after_date.timestamp())
    before_date = after_date + timedelta(days=100)
    before_date_unix = int(before_date.timestamp())
    all_activities_list = []

    # Fetch valid access token
    strava_access_token = check_token_expiry(spark = spark, client_id = client_id, scope = scope, catalog = catalog, 
                                             schema = schema, token_table = token_table, secure_path = secure_path)
    print("Getting all Strava activities from Strava API...")

    while True:
        response = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers = {"Authorization": f"Bearer {strava_access_token}"},
            params = {
                "before": before_date_unix,
                "after": after_date_unix,
                "per_page": 100
            }
        )
        activities = response.json()
        all_activities_list.append(activities)
        after_date_unix = before_date_unix
        if after_date_unix >= time.time():
            break
        before_date = before_date + timedelta(days=100)
        before_date_unix = int(before_date.timestamp())
    print("All Strava activities fetched successfully.")
    return all_activities_list


def convert_api_response_to_df(spark, response):
    """
    Convert Strava API response to Spark DataFrame.
    Parameters:
    - spark (SparkSession): Spark session object.
    - response (dict): Strava API response.
    Returns:
    - DataFrame: Spark DataFrame containing Strava activities.
    """
    payload = response.text
    json_df = spark.createDataFrame([(payload,)], ["json_str"])

    # Infer a Spark schema from the JSON string and parse it
    parsed_df = json_df.select(
        from_json(col("json_str"), schema_of_json(lit(payload))).alias("data")
    )
    flattened_df = parsed_df.select(explode('data').alias('athlete_activities'))

    flattened_variant_df = flattened_df.select(from_json(to_json('athlete_activities'), 'variant').alias('athlete_activities'))
    return flattened_variant_df

        