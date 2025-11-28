from src.utils.strava_api_utils import get_athlete_profile_details

from pyspark.sql.functions import *
from pyspark.sql.types import *
import yaml
import argparse
import sys
import logging

config = None

def main():
    # declare global variables
    global config

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file_name', required = True, help = 'environment config file name e.g. dev_config.yaml for dev environment')
    args = parser.parse_args()
    config_file_name = args.config_file_name

    # Load configuration from YAML file
    with open(f'src/resources/config/{config_file_name}', 'r') as f:
        config = yaml.safe_load(f)
    
    # Get Strava athlete profile details from Strava API
    strava_client_id = config['strava_api']['client_id']
    athlete_profile_scope = config['strava_api']['athlete_profile_scope']
    catalog = config['databricks']['catalog_name']
    schema = config['databricks']['schema_name']
    token_table = config['databricks']['token_table']['token_table_name']
    athlete_profile_data = get_athlete_profile_details(
        client_id = strava_client_id,
        scope = athlete_profile_scope,
        catalog = catalog,
        schema = schema,
        token_table = token_table
    )

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