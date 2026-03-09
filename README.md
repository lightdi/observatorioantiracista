# Observatório de Práticas Antirracistas (OPA)

Portal em Flask com blog, denúncias e painel administrativo. Layout inspirado no observatório antirracista, com cores temáticas (Indígenas, Afro-Brasileiros, Ciganos/Roma, Cultura & Resistência).

## Stack

- **Flask** + Jinja2 + Bootstrap 5
- **SQLite** (padrão) ou **PostgreSQL** (SQLAlchemy, Flask-Migrate)
- **Flask-WTF**, **Flask-Login**
- Mínimo de JavaScript (apenas alertas e Bootstrap)

## Estrutura

```
observatorioantiracista/
├── config.py           # Configurações (DB, SECRET_KEY)
├── app/
│   ├── __init__.py     # Application Factory, Blueprints
│   ├── models.py       # User, Post, Denuncia
│   ├── extensões.py    # db, login_manager, migrate
│   ├── static/         # css, img, js
│   ├── templates/      # base.html, admin_base.html, _macros.html, errors/
│   ├── blue_main/      # Site público (início, artigos, denúncia, contato)
│   └── blue_admin/     # Painel admin (login, posts, denúncias)
├── migrations/         # Flask-Migrate (gerado com flask db init)
├── requirements.txt
├── run.py              # Desenvolvimento: python run.py
├── wsgi.py             # Produção (Gunicorn/uWSGI)
└── .env.example        # Copiar para .env
```

## Como rodar

### 1. Ambiente virtual e dependências

```bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Banco de dados

**Padrão (SQLite):** Sem configuração. O arquivo `instance/opa.db` é criado automaticamente.

**PostgreSQL:** Defina `DATABASE_URL` no `.env` para usar PostgreSQL:

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/observatorio_opa
```

Copie `.env.example` para `.env` e preencha (SECRET_KEY é recomendado).

### 3. Migrations

```bash
set FLASK_APP=run.py
flask db init
flask db migrate -m "tabelas iniciais"
flask db upgrade
```

### 4. Usuário admin

```bash
python scripts/criar_admin.py
```

Login: `admin` / Senha: `admin123` (altere após o primeiro acesso).

### 5. Servidor de desenvolvimento

```bash
python run.py
```

- Site: http://127.0.0.1:5000/  
- Admin: http://127.0.0.1:5000/admin/ (faça login)

## Rotas principais

| Rota | Descrição |
|------|-----------|
| `/` | Página inicial (hero, destaques, últimas notícias, áreas de atuação) |
| `/artigos` | Listagem de posts |
| `/post/<slug>` | Post único |
| `/denunciar` | Formulário de denúncia |
| `/contato` | Contato |
| `/buscar?q=` | Busca no blog |
| `/admin` | Painel (login, dashboard, posts, denúncias) |

## Cores temáticas (CSS)

Classes em `static/css/style.css`:

- **Indígenas**: verde (`--opa-verde`)
- **Afro-Brasileiros**: preto (`--opa-preto`)
- **Ciganos/Roma**: amarelo/laranja (`--opa-amarelo`, `--opa-laranja`)
- **Cultura & Resistência**: vermelho (`--opa-vermelho`)

Nos templates, use `card-{{ post.categoria_slug }}` para aplicar a cor ao card.
