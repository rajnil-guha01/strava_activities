CREATE OR REPLACE FUNCTION data_engineering.strava_dev.mask_strava_tokens(token STRING) 
RETURN 
  CASE 
    WHEN current_user() != 'rajnil94.guha@gmail.com' THEN '***-**-****' 
    ELSE token 
  END;