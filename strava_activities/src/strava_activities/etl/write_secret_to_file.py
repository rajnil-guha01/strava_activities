import os
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--secret_path', required = True, help = 'Path to the secret file.')
    parser.add_argument('--strava_secret_scope', required = True, help = 'DBX secret scope name.')
    parser.add_argument('--strava_client_secret_name', required = True, help = 'DBX secret name for Strava client secret.')
    args = parser.parse_args()

    print("Writing Strava client secret to file...")

    secure_path = args.secret_path
    strava_secret_scope = args.strava_secret_scope
    strava_client_secret_name = args.strava_client_secret_name

    strava_client_secret = dbutils.secrets.get(scope = strava_secret_scope, key = strava_client_secret_name)

    # Write the secret to the specified file
    with open(secure_path, "w") as f:
        f.write(strava_client_secret)
    
    print(f"Strava client secret written to file successfully.")

if __name__ == "__main__":
    main()