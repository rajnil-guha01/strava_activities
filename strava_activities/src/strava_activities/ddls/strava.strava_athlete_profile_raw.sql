CREATE TABLE data_engineering_prod.strava.strava_athlete_profile_raw (
  athlete_profile VARIANT COMMENT 'Contains detailed information about the athlete, including their name, age, and other relevant personal data that can help in understanding their performance and activity levels.',
  run_date DATE COMMENT 'Represents the specific date on which the athlete engaged in running activities, allowing for time-based analysis of performance and trends.',
  run_time TIMESTAMP COMMENT 'Indicates the exact timestamp of when the running activity took place, which can be useful for tracking the duration and timing of workouts.')
USING delta
COMMENT 'The table contains raw data related to athlete profiles from Strava. It includes information about the athlete, the date of their activities, and the timestamp for when these activities occurred. This data can be used for analyzing athlete performance trends, understanding activity patterns over time, and integrating with other fitness-related datasets.'
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