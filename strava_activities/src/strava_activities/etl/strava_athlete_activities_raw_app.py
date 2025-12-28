from strava_activities.utils.strava_api_utils import get_strava_activities, convert_api_response_to_df
from strava_activities.utils.common_utils import get_config_file_path

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime, timedelta
import time
import yaml
import argparse
import sys

config = None

def main():
    # declare global variables
    global config

    # Define Spark session
    spark = SparkSession.builder \
        .appName("Strava Athlete Activities Pipeline") \
        .getOrCreate()

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file_name', required = True, help = 'environment config file name e.g. dev_config.yaml for dev environment')
    parser.add_argument('--secret_path', required = True, help = 'Path to the secret file.')
    parser.add_argument('--job_run_date', required = True, help = 'Job run date. Format: YYYY-MM-DD')
    parser.add_argument('--job_run_time', required = True, help = 'Job run time. Format: YYYY-MM-DDTHH:MM:SS')
    parser.add_argument('--load_type', required = True, help = 'Type of load: full(F) or incremental(I)')
    args = parser.parse_args()
    config_file_name = args.config_file_name
    secure_path = args.secret_path
    run_date = args.job_run_date
    run_time = args.job_run_time
    load_type = args.load_type.upper()

    print(f"Job run date: {run_date}")
    print(f"Job run time: {run_time}")

    # Load configuration from YAML file
    config_file_absolute_path = get_config_file_path(config_file_name = config_file_name)
    with open(config_file_absolute_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Get Strava athlete activities from Strava API
    strava_client_id = config['strava_api']['client_id']
    athlete_profile_scope = config['strava_api']['athlete_profile_scope']
    catalog = config['databricks']['catalog_name']
    schema = config['databricks']['schema_name']
    token_table = config['databricks']['token_table']['token_table_name']

    try:
        if load_type == 'I':
            print('Performing incremental load...')
            before_date_unix = int(datetime.strptime(run_time, "%Y-%m-%dT%H:%M:%S.%f").timestamp())
            after_date = datetime.strptime(run_time, "%Y-%m-%dT%H:%M:%S.%f") - timedelta(days=7)
            after_date_unix = int(after_date.timestamp())
            athlete_activities_data = get_strava_activities(
                spark = spark,
                client_id = strava_client_id,
                scope = athlete_profile_scope,
                catalog = catalog,
                schema = schema,
                token_table = token_table,
                before_date_unix = before_date_unix,
                after_date_unix = after_date_unix,
                secure_path = secure_path,
                load_type = load_type
            )
            athlete_activities_df = convert_api_response_to_df(spark = spark, response = athlete_activities_data)

        else:
            print('Performing full load...')
            after_date = datetime.strptime("2024-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
            after_date_unix = int(after_date.timestamp())
            before_date = after_date + timedelta(days = 100)
            before_date_unix = int(before_date.timestamp())
            final_schema = StructType([
                StructField('athlete_activities', VariantType())
            ])
            athlete_activities_df = spark.createDataFrame([], schema = final_schema)

            while True:
                athlete_activities_data = get_strava_activities(
                    spark = spark,
                    client_id = strava_client_id,
                    scope = athlete_profile_scope,
                    catalog = catalog,
                    schema = schema,
                    token_table = token_table,
                    before_date_unix = before_date_unix,
                    after_date_unix = after_date_unix,
                    secure_path = secure_path,
                    load_type = load_type
                )
                part_activities_df = convert_api_response_to_df(spark = spark, response = athlete_activities_data)
                athlete_activities_df = athlete_activities_df.union(part_activities_df)

                after_date_unix = before_date_unix
                if after_date_unix >= time.time():
                    break
                before_date = before_date + timedelta(days = 100)
                before_date_unix = int(before_date.timestamp())


    except Exception as e:
        print("Error while fetching athlete activities details from Strava API:", str(e))
        sys.exit(1)
    
    # Write athlete activities data to raw table
    athlete_activities_df = athlete_activities_df.withColumn('run_date', lit(run_date).cast('date')) \
            .withColumn('run_time', lit(run_time).cast('timestamp'))
    raw_table = config['databricks']['athlete_activities']['raw_table']['raw_table_name']
    raw_table_name = f"{catalog}.{schema}.{raw_table}"
    athlete_activities_df.write.format('delta').mode('append').saveAsTable(raw_table_name)
    print(f"Athlete activities data written to raw table: {raw_table_name}")

if __name__ == '__main__':
    main()
