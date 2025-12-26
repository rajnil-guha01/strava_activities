CREATE TABLE data_engineering.strava_dev.cal_dim (
  id BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1),
  cal_date DATE,
  cal_day INT,
  cal_month INT,
  cal_year INT,
  cal_day_of_week INT,
  cal_day_name STRING,
  cal_week_of_year INT,
  cal_month_name STRING,
  cal_quarter INT,
  is_weekend BOOLEAN,
  last_day_of_month DATE)
USING delta
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
  'delta.writePartitionColumnsToParquet' = 'true')