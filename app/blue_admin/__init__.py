"""
Blueprint do painel administrativo: login, posts, denúncias.
"""
from flask import Blueprint

blue_admin = Blueprint("blue_admin", __name__, template_folder="templates")

from app.blue_admin import routes  # noqa: E402, F401
