#!/bin/sh
yoyo apply --database postgresql://${DB_LOGIN}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME} ./migration/
uvicorn controller.main:app --host 0.0.0.0 --port 8080