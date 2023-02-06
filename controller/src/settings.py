import os

# AUTH
COOKIE_AUTHORIZATION_NAME = "SESSION_TOKEN"
COOKIE_DOMAIN = "localhost"

PROTOCOL = "http://"
FULL_HOST_NAME = "localhost"
PORT_NUMBER = 8000

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRETS_JSON = "src/client_secret_google.json"
SCOPES = ["https://www.googleapis.com/auth/userinfo.email",
'https://www.googleapis.com/auth/userinfo.profile']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v2'

API_LOCATION = f"{PROTOCOL}{FULL_HOST_NAME}:{PORT_NUMBER}"
SWAP_TOKEN_ENDPOINT = "/swap_token"
SUCCESS_ROUTE = "/users/me"
ERROR_ROUTE = "/login_error"

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

COUNT_IRREGULAR_VERBS_LEVEL_1 = 50
COUNT_IRREGULAR_VERBS_LEVEL_2 = 135



DATABASE = {
    'default': {
        'NAME': os.environ.get('DB_NAME'),
        'LOGIN': os.environ.get('DB_LOGIN'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    },
    'poolSize': 10
}