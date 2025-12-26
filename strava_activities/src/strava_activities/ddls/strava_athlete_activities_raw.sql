CREATE TABLE data_engineering_prod.strava.strava_athlete_activities_raw (
  athlete_activities VARIANT COMMENT 'Contains detailed information about the various activities performed by athletes, including types of activities and metrics associated with each one.',
  run_date DATE COMMENT 'Represents the specific date on which the activity took place, allowing for time-based analysis of athlete performance.',
  run_time TIMESTAMP COMMENT 'Records the exact date and time when the activity was logged, which is essential for understanding the timing and duration of each athlete\'s performance.')
USING delta
COMMENT 'The table contains raw data related to athlete activities from Strava. It includes details about various activities performed by athletes, along with the date and time of each activity. This data can be used for analyzing athlete performance, tracking activity trends over time, and understanding participation patterns.'
TBLPROPERTIES (
  'delta.enableDeletionVectors' = 'true',
  'delta.enableRowTracking' = 'true',
  'delta.feature.appendOnly' = 'supported',
  'delta.feature.deletionVectors' = 'supported',
  'delta.feature.domainMetadata' = 'supported',
  'delta.feature.invariants' = 'supported',
  'delta.feature.rowTracking' = 'supported',
  'delta.feature.variantType-preview' = 'supported',
  'delta.minReaderVersion' = '3',
  'delta.minWriterVersion' = '7',
  'delta.parquet.compression.codec' = 'zstd',
  'delta.writePartitionColumnsToParquet' = 'true')
