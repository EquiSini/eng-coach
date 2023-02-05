# syntax=docker/dockerfile:1
FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt


ARG HOST
ARG DB_PORT
ARG DB_LOGIN
ARG DB_PASSWORD
ARG DB_NAME

# Mount valume
COPY . /app
COPY ./migration/ ./migration/

# Final image
# COPY ./src /app/controller
# CMD ["uvicorn", "controller.main:controller", "--host", "0.0.0.0", "--port", "8080"]