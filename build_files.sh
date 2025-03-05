#!/bin/bash

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Making migrations..."
python manage.py makemigrations
python manage.py makemigrations financas_pessoais
python manage.py makemigrations financas_juridicas
python manage.py makemigrations usuarios

echo "Applying migrations..."
python manage.py migrate
python manage.py migrate auth
python manage.py migrate admin
python manage.py migrate sessions
python manage.py migrate financas_pessoais
python manage.py migrate financas_juridicas
python manage.py migrate usuarios

echo "Creating superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
END 