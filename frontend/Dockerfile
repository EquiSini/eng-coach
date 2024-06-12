FROM node:alpine

WORKDIR /usr/src/app

COPY . /usr/src/app

RUN npm install -g @angular/cli

RUN npm install

ARG YANDEX_CLIENT_ID
ARG GOOGLE_CLIENT_ID
ARG BACKEND_URL

RUN sed -i -e "s#!YANDEX_CLIENT_ID#${YANDEX_CLIENT_ID}#g" /usr/src/app/src/environments/environment.ts
RUN sed -i -e "s#!GOOGLE_CLIENT_ID#${GOOGLE_CLIENT_ID}#g" /usr/src/app/src/environments/environment.ts
RUN sed -i -e "s#!BACKEND_URL#${BACKEND_URL}#g" /usr/src/app/src/environments/environment.ts

RUN sed -i -e "s#!YANDEX_CLIENT_ID#${YANDEX_CLIENT_ID}#g" /usr/src/app/src/environments/environment.development.ts
RUN sed -i -e "s#!GOOGLE_CLIENT_ID#${GOOGLE_CLIENT_ID}#g" /usr/src/app/src/environments/environment.development.ts
RUN sed -i -e "s#!BACKEND_URL#${BACKEND_URL}#g" /usr/src/app/src/environments/environment.development.ts

EXPOSE 4200

CMD ["ng", "serve", "--host", "0.0.0.0", "--poll", "1000"]

