from strava_activities.utils.common_utils import get_config_file_path

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import Window
import yaml
import argparse
import sys

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
    
    catalog = config['databricks']['catalog_name']
    schema = config['databricks']['schema_name']
    raw_table_name = config['databricks']['athlete_profile']['raw_table']['raw_table_name']
    raw_table = f"{catalog}.{schema}.{raw_table_name}"
    cleanse_table_name = config['databricks']['athlete_profile']['cleanse_table']['cleanse_table_name']
    cleanse_table = f"{catalog}.{schema}.{cleanse_table_name}"

    # Read data from raw table for this run date and apply transformations
    raw_df = spark.sql(f"select * from {raw_table} where run_date = '{run_date}'")
    print('Read raw athlete profile data from table:', raw_table)

    cleanse_df = raw_df.selectExpr(
        "cast(athlete_profile:id as int) as id",
        "trim(cast(athlete_profile:firstname as string)) as first_name",
        "trim(cast(athlete_profile:lastname as string)) as last_name",
        "cast(athlete_profile:badge_type_id as int) as badge_type_id",
        "trim(cast(athlete_profile:bio as string)) as bio",
        "trim(cast(athlete_profile:city as string)) as city",
        "trim(cast(athlete_profile:state as string)) as state",
        "trim(cast(athlete_profile:country as string)) as country",
        "cast(athlete_profile:premium as boolean) as premium",
        "cast(athlete_profile:profile as string) as profile",
        "cast(athlete_profile:profile_medium as string) as profile_medium",
        "cast(athlete_profile:resource_state as int) as resource_state",
        "cast(athlete_profile:sex as string) as sex",
        "cast(athlete_profile:summit as boolean) as summit",
        "cast(athlete_profile:weight as float) as weight",
        "cast(athlete_profile:created_at as timestamp) as created_at",
        "cast(athlete_profile:updated_at as timestamp) as updated_at",
        "run_date",
        "run_time"
    )

    window_spec = Window.partitionBy('id').orderBy(col('updated_at').desc())
    final_df = cleanse_df.withColumn('rn', row_number().over(window_spec)) \
        .filter("rn = 1") \
        .drop('rn')
    
    # Write the cleansed data to cleanse table
    final_df.write.mode('overwrite') \
        .format('delta') \
        .option('mergeSchema', 'true') \
        .option('replaceWhere', f"run_date = '{run_date}'") \
        .saveAsTable(cleanse_table)
    
    print(f"Cleansed athlete profile data written to table: {cleanse_table} for run date: {run_date}")

if __name__ == '__main__':
    main()





