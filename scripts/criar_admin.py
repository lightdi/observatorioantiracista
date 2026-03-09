"""
Script para criar o primeiro usuário administrador.
Uso: python -m scripts.criar_admin
Execute a partir da raiz do projeto. Requer banco criado e migrations aplicadas.
"""
import os
import sys

# Garantir que o diretório raiz está no path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensões import db
from app.models import User

def main():
    app = create_app()
    with app.app_context():
        if User.query.filter_by(username="admin").first():
            print("Usuário 'admin' já existe.")
            return
        user = User(username="admin", email="admin@opa.local")
        user.set_password("admin123")  # Altere na primeira entrada!
        db.session.add(user)
        db.session.commit()
        print("Usuário 'admin' criado. Senha: admin123 — altere após o primeiro login.")

if __name__ == "__main__":
    main()
