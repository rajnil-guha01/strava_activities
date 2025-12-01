from strava_activities.utils.strava_api_utils import get_athlete_profile_details
from strava_activities.utils.common_utils import get_config_file_path

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import yaml
import argparse
import sys
import logging
from pathlib import Path

config = None

def main():
    # declare global variables
    global config

    # Define Spark session
    spark = SparkSession.builder \
        .appName("Strava Athlete Profile Pipeline") \
        .getOrCreate()

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file_name', required = True, help = 'environment config file name e.g. dev_config.yaml for dev environment')
    args = parser.parse_args()
    config_file_name = args.config_file_name

    # Load configuration from YAML file
    config_file_absolute_path = get_config_file_path(config_file_name = config_file_name)
    with open(config_file_absolute_path, 'r') as f:
        config = yaml.safe_load(f)

    # Get Strava athlete profile details from Strava API
    strava_client_id = config['strava_api']['client_id']
    athlete_profile_scope = config['strava_api']['athlete_profile_scope']
    catalog = config['databricks']['catalog_name']
    schema = config['databricks']['schema_name']
    token_table = config['databricks']['token_table']['token_table_name']
    strava_dbx_secret_scope = config['databricks']['secret_scope']

    try:
        athlete_profile_data = get_athlete_profile_details(
            spark = spark,
            client_id = strava_client_id,
            scope = athlete_profile_scope,
            catalog = catalog,
            schema = schema,
            token_table = token_table,
            secret_scope = strava_dbx_secret_scope
        )
    except Exception as e:
        print(f"Error fetching athlete profile details: {e}")
        sys.exit(0)

    # Convert athlete profile data to Spark DataFrame and write data to raw table
    athlete_profile_df = spark.createDataFrame([athlete_profile_data], schema = ['json_data'])
    athlete_profile_df = athlete_profile_df.withColumn('athlete_profile', from_json(to_json('json_data'), 'variant')) \
        .withColumn('load_ts', current_timestamp()) \
        .drop('json_data')
    
    raw_table = config['databricks']['raw_table']['raw_table_name']
    raw_table_name = f"{catalog}.{schema}.{raw_table}"
    athlete_profile_df.write.format('delta').mode('append').saveAsTable(raw_table_name)
    print(f"Athlete profile data written to raw table: {raw_table_name}")

if __name__ == '__main__':
    main()