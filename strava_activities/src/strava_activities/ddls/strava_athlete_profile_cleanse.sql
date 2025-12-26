CREATE TABLE data_engineering_prod.strava.strava_athlete_profile_cleanse (
  id INT COMMENT 'A unique identifier for each athlete profile, allowing for easy reference and data management.',
  first_name STRING COMMENT 'The first name of the athlete, useful for personalizing communications and marketing efforts.',
  last_name STRING COMMENT 'The last name of the athlete, which can be used in conjunction with the first name for full identification.',
  badge_type_id INT COMMENT 'An identifier representing the type of badge the athlete has earned, which can indicate their level of engagement or achievement.',
  bio STRING COMMENT 'A brief biography of the athlete, providing insights into their background, interests, and motivations.',
  city STRING COMMENT 'The city where the athlete is located, which can help in understanding regional demographics and preferences.',
  state STRING COMMENT 'The state of residence for the athlete, useful for regional analysis and targeted marketing strategies.',
  country STRING COMMENT 'The country of the athlete, providing a broader context for demographic analysis and international engagement.',
  premium BOOLEAN COMMENT 'Indicates whether the athlete has a premium membership, which can be relevant for understanding user engagement and potential revenue.',
  profile STRING COMMENT 'A URL link to the athlete\'s profile picture, useful for visual representation in reports and marketing materials.',
  profile_medium STRING COMMENT 'A URL link to a medium-sized version of the athlete\'s profile picture, suitable for various display contexts.',
  resource_state INT COMMENT 'An integer representing the state of the resource, which can be used for tracking changes or updates to the athlete\'s profile.',
  sex STRING COMMENT 'The gender of the athlete, which can be important for demographic analysis and tailoring content to specific audiences.',
  summit BOOLEAN COMMENT 'Indicates whether the athlete is part of the Summit program, which may reflect their level of commitment and engagement with the platform.',
  weight FLOAT COMMENT 'The weight of the athlete, which can be relevant for performance analysis and personalized training recommendations.',
  created_at TIMESTAMP COMMENT 'The timestamp indicating when the athlete\'s profile was created, useful for tracking user growth and engagement over time.',
  updated_at TIMESTAMP COMMENT 'The timestamp of the last update made to the athlete\'s profile, important for maintaining data accuracy and relevance.',
  run_date DATE COMMENT 'The date of the athlete\'s last recorded run, which can be used to analyze activity trends and engagement levels.',
  run_time TIMESTAMP COMMENT 'The timestamp of when the athlete\'s last run was recorded, providing insights into their activity patterns and frequency.')
USING delta
COMMENT 'The table contains cleaned profiles of athletes from Strava. It includes personal information such as names, location, and bio, as well as details about their membership status and physical attributes. This data can be used for analyzing athlete demographics, understanding user engagement, and tailoring marketing strategies.'
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
  'delta.writePartitionColumnsToParquet' = 'true')