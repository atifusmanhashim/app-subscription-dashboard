import os
import secrets

def generate_secret_key(length=50):
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(length))

def write_secret_key_to_env_file(secret_key):
    env_file_path = '.env'
    with open(env_file_path, 'a') as f:
        f.write(f'SECRET_KEY={secret_key}\n')

if __name__ == "__main__":
    secret_key = generate_secret_key()
    write_secret_key_to_env_file(secret_key)
    print("SECRET_KEY generated and written to .env file successfully.")
