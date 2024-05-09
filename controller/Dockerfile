# syntax=docker/dockerfile:1
FROM python:3.9

COPY requirements.txt /app/
COPY run.sh /app/
COPY run.sh /app/
COPY ./migration/ /app/migration/

WORKDIR /app

RUN chmod 777 /app/run.sh
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

ARG DB_HOST
ARG DB_PORT
ARG DB_LOGIN
ARG DB_PASSWORD
ARG DB_NAME

# Final image
# COPY ./src /app/controller

CMD ["sh", "./run.sh"]

# CMD ["uvicorn", "controller.main:controller", "--host", "0.0.0.0", "--port", "8080"]