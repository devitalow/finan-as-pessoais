# Finanças App

Um aplicativo web para gerenciamento de finanças pessoais e jurídicas, desenvolvido com Django.

## Funcionalidades

### Finanças Pessoais
- Dashboard com visão geral das finanças
- Gerenciamento de categorias de receitas e despesas
- Gerenciamento de contas (corrente, poupança, investimentos, etc.)
- Registro e acompanhamento de transações financeiras
- Relatórios e gráficos

### Finanças Jurídicas
- Dashboard com visão geral das finanças da empresa
- Gerenciamento de empresas
- Gerenciamento de categorias de receitas e despesas
- Gerenciamento de contas bancárias
- Registro e acompanhamento de transações financeiras
- Controle de impostos e obrigações fiscais
- Relatórios e gráficos

## Tecnologias Utilizadas

- Python 3.x
- Django 5.x
- Bootstrap 5
- JavaScript
- HTML5/CSS3
- SQLite (desenvolvimento) / PostgreSQL (produção)

## Instalação

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/financas-app.git
cd financas-app
```

2. Crie e ative um ambiente virtual:
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```
pip install -r requirements.txt
```

4. Execute as migrações:
```
python manage.py migrate
```

5. Crie um superusuário:
```
python manage.py createsuperuser
```

6. Inicie o servidor de desenvolvimento:
```
python manage.py runserver
```

7. Acesse o aplicativo em `http://localhost:8000`

## Estrutura do Projeto

- `financas_app/`: Configurações do projeto Django
- `financas_pessoais/`: Aplicativo para gerenciamento de finanças pessoais
- `financas_juridicas/`: Aplicativo para gerenciamento de finanças jurídicas
- `usuarios/`: Aplicativo para gerenciamento de usuários
- `templates/`: Templates HTML
- `static/`: Arquivos estáticos (CSS, JavaScript, imagens)
- `media/`: Arquivos de mídia enviados pelos usuários

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes. 