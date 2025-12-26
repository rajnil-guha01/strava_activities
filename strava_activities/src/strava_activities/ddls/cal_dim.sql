CREATE TABLE data_engineering_prod.strava.cal_dim (
  id BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) COMMENT 'A unique identifier for each date entry in the calendar, facilitating easy reference and data management.',
  cal_date DATE COMMENT 'Represents the actual date, serving as the primary reference point for all other calendar attributes.',
  cal_day INT COMMENT 'Indicates the day of the month, ranging from 1 to 31, depending on the specific month.',
  cal_month INT COMMENT 'Denotes the month of the year, with values from 1 (January) to 12 (December).',
  cal_year INT COMMENT 'Represents the year associated with the date, allowing for year-over-year comparisons and analyses.',
  cal_day_of_week INT COMMENT 'Indicates the day of the week as a numerical value, where typically 1 represents Sunday and 7 represents Saturday.',
  cal_day_name STRING COMMENT 'Provides the name of the day of the week, such as \'Monday\' or \'Friday\', for easier readability.',
  cal_week_of_year INT COMMENT 'Represents the week number within the year, useful for weekly reporting and analysis.',
  cal_month_name STRING COMMENT 'Gives the name of the month, such as \'January\' or \'February\', enhancing clarity in reports.',
  cal_quarter INT COMMENT 'Indicates the quarter of the year, with values from 1 to 4, useful for financial and seasonal analyses.',
  is_weekend BOOLEAN COMMENT 'A boolean indicator showing whether the date falls on a weekend (Saturday or Sunday), useful for scheduling and planning.',
  last_day_of_month DATE COMMENT 'Represents the last date of the month, which can be important for financial reporting and month-end analyses.')
USING delta
COMMENT 'The table contains calendar-related data, providing various attributes for each date. It includes information such as the day, month, year, and day of the week, as well as indicators for weekends and the last day of the month. This data can be useful for time-based analyses, such as understanding seasonal trends, scheduling events, or analyzing user activity patterns over time.'
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