#!/bin/bash

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating necessary directories..."
mkdir -p static staticfiles media

echo "Making migrations..."
python manage.py makemigrations usuarios
python manage.py makemigrations financas_pessoais
python manage.py makemigrations financas_juridicas

echo "Applying migrations..."
python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate admin
python manage.py migrate sessions
python manage.py migrate usuarios
python manage.py migrate financas_pessoais
python manage.py migrate financas_juridicas

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Creating superuser..."
DJANGO_SUPERUSER_PASSWORD=admin123 python manage.py createsuperuser --noinput --username admin --email admin@example.com || true 