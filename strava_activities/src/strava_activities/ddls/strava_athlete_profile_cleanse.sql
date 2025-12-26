CREATE TABLE data_engineering.strava_dev.strava_athlete_profile_cleanse (
  id INT COMMENT 'A unique identifier for each athlete profile, allowing for easy reference and data management.',
  first_name STRING COMMENT 'The first name of the athlete, providing a personal touch to the profile.',
  last_name STRING COMMENT 'The last name of the athlete, which, along with the first name, helps in identifying the individual.',
  badge_type_id INT COMMENT 'An identifier for the type of badge the athlete has earned, which can indicate their achievements or status within the platform.',
  bio STRING COMMENT 'A brief biography of the athlete, offering insights into their background, interests, and athletic journey.',
  city STRING COMMENT 'The city where the athlete is located, useful for geographical analysis and community engagement.',
  state STRING COMMENT 'The state of residence for the athlete, which can help in understanding regional demographics.',
  country STRING COMMENT 'The country of the athlete, providing a broader context for demographic analysis and user engagement.',
  premium BOOLEAN COMMENT 'Indicates whether the athlete has a premium account, which can affect their access to features and services.',
  profile STRING COMMENT 'A URL link to the athlete\'s main profile picture, enhancing the visual representation of the athlete.',
  profile_medium STRING COMMENT 'A URL link to a medium-sized version of the athlete\'s profile picture, useful for various display contexts.',
  resource_state INT COMMENT 'Represents the state of the resource, which can be used to track changes or updates to the athlete\'s profile.',
  sex STRING COMMENT 'The gender of the athlete, which can be important for demographic analysis and targeted engagement.',
  summit BOOLEAN COMMENT 'Indicates whether the athlete is part of the Summit program, which may offer additional benefits and features.',
  weight FLOAT COMMENT 'The weight of the athlete, which can be relevant for performance analysis and health metrics.',
  created_at TIMESTAMP COMMENT 'The timestamp indicating when the athlete\'s profile was created, useful for tracking user growth over time.',
  updated_at TIMESTAMP COMMENT 'The timestamp for the last update made to the athlete\'s profile, helping to monitor profile activity.',
  run_date DATE COMMENT 'The date of a specific run, which can be used for performance tracking and historical analysis.',
  run_time TIMESTAMP COMMENT 'The timestamp for when the run occurred, providing detailed timing information for performance evaluation.')
USING delta
COMMENT 'The table contains cleaned profiles of athletes from Strava. It includes personal information such as names, location, and bio, as well as account details like premium status and badge type. This data can be used for analyzing athlete demographics, understanding user engagement, and enhancing user experience on the platform.'
CLUSTER BY (run_date)
TBLPROPERTIES (
  'delta.checkpointPolicy' = 'v2',
  'delta.enableDeletionVectors' = 'true',
  'delta.enableRowTracking' = 'true',
  'delta.feature.appendOnly' = 'supported',
  'delta.feature.deletionVectors' = 'supported',
  'delta.feature.invariants' = 'supported',
  'delta.feature.rowTracking' = 'supported',
  'delta.feature.v2Checkpoint' = 'supported',
  'delta.parquet.compression.codec' = 'zstd',
  'delta.workloadBasedColumns.optimizerStatistics' = '`run_date`',
  'delta.writePartitionColumnsToParquet' = 'true')