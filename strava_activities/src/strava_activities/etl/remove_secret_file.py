import os
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--secret_path', required = True, help = 'Path to the secret file.')

    args = parser.parse_args()
    secure_path = args.secret_path
    if os.path.exists(secure_path):
        print("Removing secret file...")
        os.remove(secure_path)
        print(f"Secret file removed successfully.")
    else:
        print("Secret file does not exist. No action needed.")

if __name__ == "__main__":
    main()