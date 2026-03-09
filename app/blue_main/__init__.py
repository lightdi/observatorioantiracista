"""
Blueprint da parte pública do site: blog, destaques, contato, denúncia.
"""
from flask import Blueprint

blue_main = Blueprint("blue_main", __name__, template_folder="templates")

from app.blue_main import routes  # noqa: E402, F401
