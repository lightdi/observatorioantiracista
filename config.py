"""
Configurações do Flask para o Observatório de Práticas Antirracistas (OPA).
Variáveis sensíveis devem ser definidas via variáveis de ambiente (.env).

Banco de dados:
- Sem DATABASE_URL: usa SQLite (instance/opa.db) — ideal para desenvolvimento.
- Com DATABASE_URL: usa PostgreSQL — para produção ou quando configurado.
"""
import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent
SQLITE_PATH = BASE_DIR / "instance" / "opa.db"


def _database_uri():
    """Retorna PostgreSQL se DATABASE_URL estiver definida, senão SQLite."""
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        return url
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{SQLITE_PATH.as_posix()}"


class Config:
    """Configuração base."""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-altere-em-producao"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Número de itens por página (blog, denúncias)
    POSTS_PER_PAGE = 9
    DENUNCIAS_PER_PAGE = 20


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento. SQLite por padrão."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = _database_uri()


class ProductionConfig(Config):
    """Configuração para produção. Use DATABASE_URL para PostgreSQL."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = _database_uri()


class TestingConfig(Config):
    """Configuração para testes."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
