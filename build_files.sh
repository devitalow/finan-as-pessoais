# Instala as dependências
pip install -r requirements.txt

# Coleta arquivos estáticos
python manage.py collectstatic --noinput

# Gera as migrações (caso tenha alguma pendente)
python manage.py makemigrations

# Aplica as migrações
python manage.py migrate --noinput

# Cria um superusuário se não existir
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell 