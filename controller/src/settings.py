import os

# AUTH
COOKIE_AUTHORIZATION_NAME = "Authorization"
COOKIE_DOMAIN = "localhost"

PROTOCOL = "http://"
FULL_HOST_NAME = "localhost"
PORT_NUMBER = 8000

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRETS_JSON = "client_secret_google.json"

API_LOCATION = f"{PROTOCOL}{FULL_HOST_NAME}:{PORT_NUMBER}"
SWAP_TOKEN_ENDPOINT = "/swap_token"
SUCCESS_ROUTE = "/users/me"
ERROR_ROUTE = "/login_error"

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30





DATABASE = {
    'default': {
        'NAME': os.environ.get('DB_NAME'),
        'LOGIN': os.environ.get('DB_LOGIN'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    },
    'poolSize': 5
}