"""
Script para rodar a aplicação em desenvolvimento.
Uso: python run.py   ou   flask run (com FLASK_APP=run.py ou wsgi:app)
"""
import os
from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", True))
