CREATE TABLE data_engineering.strava_dev.strava_athelete_tokens (
  id BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) COMMENT 'A unique identifier for each token entry, allowing for easy reference and management of individual records.',
  athlete_id STRING COMMENT 'Represents the unique identifier of the athlete associated with the token, linking the token to a specific user in the Strava system.',
  scope STRING COMMENT 'Indicates the level of access granted by the token, defining what actions the token holder can perform within the Strava API.',
  access_token STRING COMMENT 'Contains the token used to authenticate API requests on behalf of the athlete, enabling access to their data and functionalities.' MASK `data_engineering`.`strava_dev`.`mask_strava_tokens`,
  expires_at INT COMMENT 'Specifies the timestamp indicating when the access token will expire, which is crucial for managing token refresh and ensuring uninterrupted access.',
  refresh_token STRING COMMENT 'Holds the token that can be used to obtain a new access token once the current one expires, ensuring continued access without requiring the athlete to re-authenticate.' MASK `data_engineering`.`strava_dev`.`mask_strava_tokens`)
USING delta
COMMENT 'The table contains information about athlete tokens used for accessing the Strava API. It includes details such as the athlete\'s ID, the scope of access, and the tokens themselves, including access and refresh tokens along with their expiration time. This data can be used for managing API access for athletes, tracking token validity, and ensuring secure interactions with the Strava platform.'
TBLPROPERTIES (
  'delta.enableDeletionVectors' = 'true',
  'delta.feature.appendOnly' = 'supported',
  'delta.feature.deletionVectors' = 'supported',
  'delta.feature.domainMetadata' = 'supported',
  'delta.feature.identityColumns' = 'supported',
  'delta.feature.invariants' = 'supported',
  'delta.feature.rowTracking' = 'supported',
  'delta.minReaderVersion' = '3',
  'delta.minWriterVersion' = '7',
  'delta.parquet.compression.codec' = 'zstd')