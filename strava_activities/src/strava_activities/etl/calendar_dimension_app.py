from strava_activities.utils.common_utils import get_config_file_path

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
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
    args = parser.parse_args()
    config_file_name = args.config_file_name

    # Load configuration from YAML file
    config_file_absolute_path = get_config_file_path(config_file_name = config_file_name)
    with open(config_file_absolute_path, 'r') as f:
        config = yaml.safe_load(f)

    # Read and transform strava activities raw data
    catalog = config['databricks']['catalog_name']
    schema = config['databricks']['schema_name']
    cal_table_name = config['databricks']['calendar_dimension']['table_name']
    cal_dim_table = f"{catalog}.{schema}.{cal_table_name}"

    cal_dim_df = spark.sql("""
    with calendar_dates as (
        select
        explode(sequence(to_date('2024-01-01'), to_date('2500-12-31'), interval 1 day)) as cal_date
    )
    select
        cal_date,
        day(cal_date) as cal_day,
        month(cal_date) as cal_month,
        year(cal_date) as cal_year,
        dayofweek(cal_date) as cal_day_of_week,
        dayname(cal_date) as cal_day_name,
        weekofyear(cal_date) as cal_week_of_year,
        monthname(cal_date) as cal_month_name,
        quarter(cal_date) as cal_quarter,
        case
            when dayofweek(cal_date) in (1, 7) then true 
            else false
        end as is_weekend,
        last_day(cal_date) as last_day_of_month
    from calendar_dates
    order by cal_date
    """)

    # Write to calendar dimension delta table
    cal_dim_df.write.format('delta').mode('overwrite').saveAsTable(cal_dim_table)
    print(f'Wrote calendar dimension data to table: {cal_dim_table}')

if __name__ == "__main__":
    main()

