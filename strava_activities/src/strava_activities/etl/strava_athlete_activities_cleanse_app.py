from strava_activities.utils.common_utils import get_config_file_path

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import Window
from delta.tables import DeltaTable
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
    parser.add_argument('--job_run_date', required = True, help = 'Job run date. Format: YYYY-MM-DD')
    parser.add_argument('--job_run_time', required = True, help = 'Job run time. Format: YYYY-MM-DDTHH:MM:SS')
    args = parser.parse_args()
    config_file_name = args.config_file_name
    run_date = args.job_run_date
    run_time = args.job_run_time

    print(f"Job run date: {run_date}")
    print(f"Job run time: {run_time}")

    # Load configuration from YAML file
    config_file_absolute_path = get_config_file_path(config_file_name = config_file_name)
    with open(config_file_absolute_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Read and transform strava activities raw data
    catalog = config['databricks']['catalog_name']
    schema = config['databricks']['schema_name']
    raw_table_name = config['databricks']['athlete_activities']['raw_table']['raw_table_name']
    raw_table = f"{catalog}.{schema}.{raw_table_name}"
    cleanse_table_name = config['databricks']['athlete_activities']['cleanse_table']['cleanse_table_name']
    cleanse_table = f"{catalog}.{schema}.{cleanse_table_name}"

    raw_df = spark.sql(f"select * from {raw_table} where run_date = '{run_date}'")
    print(f'Read raw athlete activities data from table: {raw_table}')

    cleanse_df = raw_df.selectExpr(
            "cast(athlete_activities:id as long) as id",
            "cast(athlete_activities:athlete:id as int) as athlete_id",
            "cast(athlete_activities:athlete_count as int) as athlete_count",
            "cast(athlete_activities:average_cadence as double) as average_cadence",
            "cast(athlete_activities:average_speed as double) as average_speed",
            "cast(athlete_activities:comment_count as int) as comment_count",
            "cast(athlete_activities:commute as boolean) as is_commute",
            "cast(athlete_activities:device_name as string) as device_name",
            "cast(athlete_activities:display_hide_heartrate_option as boolean) as display_hide_heartrate_option",
            "round(cast(athlete_activities:distance as double) / 1000, 2) as distance",
            "round(cast(athlete_activities:elapsed_time as double) / 60, 2) as elapsed_time",
            "cast(athlete_activities:elev_high as double) as elev_high",
            "cast(athlete_activities:elev_low as double) as elev_low",
            "cast(athlete_activities:external_id as string) as external_id",
            "cast(athlete_activities:flagged as boolean) as is_flagged",
            "cast(athlete_activities:from_accepted_tag as boolean) as is_from_accepted_tag",
            "cast(athlete_activities:has_heartrate as boolean) as has_heartrate",
            "cast(athlete_activities:has_kudoed as boolean) as has_kudoed",
            "cast(athlete_activities:heartrate_opt_out as boolean) as is_heartrate_opt_out",
            "cast(athlete_activities:kudos_count as int) as kudos_count",
            "cast(athlete_activities:manual as boolean) as is_manual",
            "cast(athlete_activities:map:id as string) as map_id",
            "cast(athlete_activities:max_speed as double) as max_speed",
            "round(cast(athlete_activities:moving_time as double) / 60, 2) as moving_time",
            "cast(athlete_activities:name as string) as name",
            "cast(athlete_activities:photo_count as int) as photo_count",
            "cast(athlete_activities:pr_count as int) as pr_count",
            "cast(athlete_activities:private as boolean) as is_private",
            "cast(athlete_activities:resource_state as int) as resource_state",
            "cast(athlete_activities:sport_type as string) as sport_type",
            "cast(athlete_activities:start_date as timestamp) as start_date",
            "cast(athlete_activities:start_date_local as timestamp) as start_date_local",
            "cast(athlete_activities:timezone as string) as timezone",
            "cast(athlete_activities:total_elevation_gain as double) as total_elevation_gain",
            "cast(athlete_activities:total_photo_count as int) as total_photo_count",
            "cast(athlete_activities:trainer as boolean) as is_trainer",
            "cast(athlete_activities:type as string) as type",
            "cast(athlete_activities:upload_id_str as string) as upload_id",
            "cast(athlete_activities:utc_offset as int) as utc_offset",
            "cast(athlete_activities:visibility as string) as visibility",
            "cast(athlete_activities:workout_type as int) as workout_type",
            "cast(athlete_activities:average_heartrate as double) as average_heart_rate",
            "cast(athlete_activities:max_heartrate as double) as max_heart_rate"
        ) \
        .withColumn('run_date', lit(run_date).cast('date')) \
        .withColumn('run_time', lit(run_time).cast('timestamp'))
    
    window_spec = Window.partitionBy('id').orderBy(col('start_date').desc(), col('run_time').desc())
    cleanse_df = cleanse_df.withColumn('rn', row_number().over(window_spec)) \
        .filter("rn = 1") \
        .drop('rn')
    
    # Writing data into cleanse activities table using delta merge
    cleanse_df.createOrReplaceTempView('source')
    merge_sql = f"""
        MERGE WITH SCHEMA EVOLUTION INTO {cleanse_table} AS target
        USING source AS source
        ON target.id = source.id
        WHEN MATCHED THEN
            UPDATE SET *
        WHEN NOT MATCHED THEN
            INSERT *
    """
    spark.sql(merge_sql)
    print(f"Cleansed athlete activities data merged to table: {cleanse_table} for run date: {run_date} ")

if __name__ == '__main__':
    main()
    