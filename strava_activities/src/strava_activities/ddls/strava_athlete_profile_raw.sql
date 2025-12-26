CREATE TABLE data_engineering.strava_dev.strava_athlete_profile_raw (
  athlete_profile VARIANT COMMENT 'Contains detailed information about individual athletes, including their personal data and performance metrics.',
  run_date DATE COMMENT 'Represents the specific date on which the running activity took place, allowing for time-based analysis of performance.',
  run_time TIMESTAMP COMMENT 'Records the exact timestamp of when the run started, which can be useful for tracking the duration and timing of activities.')
USING delta
COMMENT 'The table contains raw data related to athlete profiles from Strava. It includes information about individual athletes, the dates of their activities, and timestamps for their runs. This data can be used for analyzing athlete performance, tracking activity trends over time, and understanding participation patterns in running.'
TBLPROPERTIES (
  'delta.enableDeletionVectors' = 'true',
  'delta.feature.appendOnly' = 'supported',
  'delta.feature.deletionVectors' = 'supported',
  'delta.feature.domainMetadata' = 'supported',
  'delta.feature.invariants' = 'supported',
  'delta.feature.rowTracking' = 'supported',
  'delta.feature.variantType-preview' = 'supported',
  'delta.minReaderVersion' = '3',
  'delta.minWriterVersion' = '7',
  'delta.parquet.compression.codec' = 'zstd')