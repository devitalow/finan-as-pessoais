# Instala as dependências
pip install -r requirements.txt

# Coleta arquivos estáticos
python manage.py collectstatic --noinput

# Aplica as migrações (opcional, pode ser feito depois)
python manage.py migrate --noinput 