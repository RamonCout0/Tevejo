# Etapa 1: build de software (gera o bundle em dist/)
FROM node:24-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

RUN npm run build

# Etapa 2: build de ambiente (nginx servindo o bundle e fazendo proxy da API)
FROM nginx:1.27-alpine

# Como template, o nginx troca ${BACKEND_URL} pelo valor do ambiente ao subir.
ENV BACKEND_URL=http://backend:8000
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist/frontend-angular/browser /usr/share/nginx/html

EXPOSE 80
