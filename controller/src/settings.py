import os

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