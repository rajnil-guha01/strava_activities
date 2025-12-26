CREATE TABLE data_engineering_prod.strava.strava_athelete_tokens (
  id BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) COMMENT 'A unique identifier for each record in the dataset, allowing for easy reference and retrieval of specific entries.',
  athlete_id STRING COMMENT 'Represents the unique identifier assigned to each athlete, linking their data across various records.',
  scope STRING COMMENT 'Indicates the level of access granted, defining the permissions associated with the access token.',
  access_token STRING COMMENT 'A token that provides temporary access to the athlete\'s data, used for authentication in API calls.' MASK `data_engineering`.`strava_dev`.`mask_strava_tokens`,
  expires_at INT COMMENT 'The timestamp indicating when the access token will expire, essential for managing token validity.',
  refresh_token STRING COMMENT 'A token used to obtain a new access token without requiring the athlete to re-authenticate, ensuring continuous access.' MASK `data_engineering`.`strava_dev`.`mask_strava_tokens`)
USING delta
COMMENT 'The table contains information about athlete access tokens for the Strava platform. It includes details such as the athlete\'s unique identifier, the access and refresh tokens, their scopes, and expiration timestamps. This data can be used to manage athlete authentication and access permissions, ensuring that the necessary data can be retrieved securely and efficiently.'
TBLPROPERTIES (
  'delta.enableDeletionVectors' = 'true',
  'delta.enableRowTracking' = 'true',
  'delta.feature.appendOnly' = 'supported',
  'delta.feature.deletionVectors' = 'supported',
  'delta.feature.domainMetadata' = 'supported',
  'delta.feature.identityColumns' = 'supported',
  'delta.feature.invariants' = 'supported',
  'delta.feature.rowTracking' = 'supported',
  'delta.minReaderVersion' = '3',
  'delta.minWriterVersion' = '7',
  'delta.parquet.compression.codec' = 'zstd',
  'delta.writePartitionColumnsToParquet' = 'true')