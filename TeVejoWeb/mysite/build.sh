#!/usr/bin/env bash
# exit on error
set -o errexit

# Change to project directory

# Install dependencies
pip install -r requirements_render.txt

# Collect static files
python manage.py collectstatic --noinput --settings=mysite.settings.production # Coloque o nome do projeto


python manage.py migrate --settings=mysite.settings.production # Coloque o nome do projeto

# Run custom command to create groups and permissions
python manage.py criar_grupos_permissoes --settings=mysite.settings.production # Coloque o nome do projeto

# Run migrations
python manage.py migrate --settings=mysite.settings.production # Coloque o nome do projeto

#Cria um superusuário com a senha definida no ambiente
python manage.py runscript createsuperuser --settings=mysite.settings.production #Coloque o nome do projeto