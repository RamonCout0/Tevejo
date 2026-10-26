# Etapa 1: build de software (gera o bundle em dist/)
FROM node:24-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

RUN npm run build

# Etapa 2: build de ambiente (nginx servindo o bundle e fazendo proxy da API)
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/frontend-angular/browser /usr/share/nginx/html

EXPOSE 80
