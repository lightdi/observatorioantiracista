"""
Application Factory do Observatório de Práticas Antirracistas (OPA).
Cria a aplicação Flask, registra Blueprints e extensões.
"""
from flask import Flask
from config import config
from app.extensões import db, login_manager, migrate
from app.models import User


def create_app(config_name=None):
    """Cria e configura a aplicação Flask."""
    if config_name is None:
        config_name = "default"
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Configuração para proxy reverso (Traefik) e hospedagem em subdiretório
    if os.environ.get("PROXY_FIX"):
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    if os.environ.get("APPLICATION_ROOT"):
        app.config["APPLICATION_ROOT"] = os.environ.get("APPLICATION_ROOT")

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)
    login_manager.login_view = "blue_main.login"
    login_manager.login_message = "Faça login para acessar esta página."
    login_manager.login_message_category = "info"

    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registrar Blueprints
    from app.blue_main import blue_main
    from app.blue_admin import blue_admin

    app.register_blueprint(blue_main, url_prefix="/")
    app.register_blueprint(blue_admin, url_prefix="/admin")

    register_error_handlers(app)

    from datetime import datetime
    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow}

    return app


def register_error_handlers(app):
    """Registra páginas de erro 404 e 500."""
    from flask import render_template

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500
