"""
Modelos de banco de dados para o Observatório de Práticas Antirracistas (OPA).
User, Post e Denúncia.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensões import db


# Categorias temáticas do blog (slug -> nome para exibição)
CATEGORIAS = {
    "indigenas": "Indígenas",
    "afro-brasileiros": "Afro-Brasileiros",
    "ciganos-roma": "Ciganos/Roma",
    "cultura-resistencia": "Cultura & Resistência",
}


def slugify(texto):
    """Gera slug a partir do título (para URLs amigáveis)."""
    import re
    texto = texto.lower().strip()
    texto = re.sub(r"[^\w\s-]", "", texto)
    texto = re.sub(r"[-\s]+", "-", texto)
    return texto.strip("-") or "post"


class User(UserMixin, db.Model):
    """Usuário do sistema."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user') # 'admin' ou 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Post(db.Model):
    """Post do blog (artigo/notícia)."""
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    conteudo = db.Column(db.Text, nullable=False)
    resumo = db.Column(db.String(500), nullable=True)  # para listagens e SEO
    imagem_url = db.Column(db.String(500), nullable=True)  # miniatura
    categoria_slug = db.Column(db.String(50), nullable=False, default="cultura-resistencia")
    publicado = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    author = db.relationship("User", backref=db.backref("posts", lazy="dynamic"))

    def save(self):
        if not self.slug:
            self.slug = slugify(self.titulo)
        db.session.add(self)
        db.session.commit()

    @property
    def categoria_nome(self):
        return CATEGORIAS.get(self.categoria_slug, self.categoria_slug)

    def __repr__(self):
        return f"<Post {self.titulo}>"


class Artigo(db.Model):
    """Artigo científico ou de opinião publicado no portal."""
    __tablename__ = "artigos"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(250), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    autor_nome = db.Column(db.String(150), nullable=False)
    resumo = db.Column(db.Text, nullable=False)
    conteudo = db.Column(db.Text, nullable=True) # ou PDF anexo
    documento_url = db.Column(db.String(500), nullable=True)
    publicado = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True) # Quem cadastrou no sistema

    def save(self):
        if not self.slug:
            self.slug = slugify(self.titulo)
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<Artigo {self.titulo}>"

class Pesquisa(db.Model):
    """Estudos e Produção de Conhecimento."""
    __tablename__ = "pesquisas"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(250), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    descricao = db.Column(db.Text, nullable=False)
    autores = db.Column(db.String(300), nullable=False)
    material_url = db.Column(db.String(500), nullable=True)
    publicado = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def save(self):
        if not self.slug:
            self.slug = slugify(self.titulo)
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<Pesquisa {self.titulo}>"

class Noticia(db.Model):
    """Notícias relacionadas ao tema."""
    __tablename__ = "noticias"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(250), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    descricao = db.Column(db.Text, nullable=False)
    imagem_url = db.Column(db.String(500), nullable=True)
    publicado = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def save(self):
        if not self.slug:
            self.slug = slugify(self.titulo)
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<Noticia {self.titulo}>"


class Denuncia(db.Model):
    """Denúncia recebida pelo portal."""
    __tablename__ = "denuncias"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=True)  # opcional (anonimato)
    email = db.Column(db.String(120), nullable=True)
    conteudo = db.Column(db.Text, nullable=False)
    local_ocorrencia = db.Column(db.String(300), nullable=True)
    data_aproximada = db.Column(db.String(50), nullable=True) # String por simplicidade ('12/05/2026', 'Mês passado')
    status = db.Column(
        db.String(20),
        nullable=False,
        default="recebida"
    )  # recebida, em_analise, concluida
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Denuncia #{self.id} {self.status}>"


class Escola(db.Model):
    """Escola ou instituição cadastrada no sistema."""
    __tablename__ = "escolas"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(2), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relação com práticas
    praticas = db.relationship("Pratica", backref="escola", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Escola {self.nome}>"


class Pratica(db.Model):
    """Prática Antirracista desenvolvida por uma escola."""
    __tablename__ = "praticas"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(250), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    categoria_slug = db.Column(db.String(50), nullable=False, default="cultura-resistencia")
    
    # Endereço e geolocalização
    endereco = db.Column(db.String(300), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    escola_id = db.Column(db.Integer, db.ForeignKey("escolas.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True) # Cadastrador
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relação com anexos
    anexos = db.relationship("AnexoPratica", backref="pratica", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def categoria_nome(self):
        return CATEGORIAS.get(self.categoria_slug, self.categoria_slug)

    def __repr__(self):
        return f"<Pratica {self.titulo}>"


class AnexoPratica(db.Model):
    """Arquivos anexados a uma prática."""
    __tablename__ = "pratica_anexos"

    id = db.Column(db.Integer, primary_key=True)
    nome_arquivo = db.Column(db.String(250), nullable=False)
    caminho_arquivo = db.Column(db.String(500), nullable=False) # Caminho relativo em uploads/
    pratica_id = db.Column(db.Integer, db.ForeignKey("praticas.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AnexoPratica {self.nome_arquivo}>"

class Comentario(db.Model):
    """Comentários de usuários em publicações públicas."""
    __tablename__ = 'comentarios'
    
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    aprovado = db.Column(db.Boolean, default=True) # Moderação
    
    # Relação com usuário
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comentarios', lazy='dynamic'))
    
    # Ligações opcionais para polimorfismo via FK
    pratica_id = db.Column(db.Integer, db.ForeignKey('praticas.id'), nullable=True)
    artigo_id = db.Column(db.Integer, db.ForeignKey('artigos.id'), nullable=True)
    pesquisa_id = db.Column(db.Integer, db.ForeignKey('pesquisas.id'), nullable=True)
    noticia_id = db.Column(db.Integer, db.ForeignKey('noticias.id'), nullable=True)
    
    # Relationships reversas para facilitar o carregamento
    pratica = db.relationship('Pratica', backref=db.backref('comentarios', lazy='dynamic', cascade='all, delete-orphan', order_by='Comentario.created_at.desc()'))
    artigo = db.relationship('Artigo', backref=db.backref('comentarios', lazy='dynamic', cascade='all, delete-orphan', order_by='Comentario.created_at.desc()'))
    pesquisa = db.relationship('Pesquisa', backref=db.backref('comentarios', lazy='dynamic', cascade='all, delete-orphan', order_by='Comentario.created_at.desc()'))
    noticia = db.relationship('Noticia', backref=db.backref('comentarios', lazy='dynamic', cascade='all, delete-orphan', order_by='Comentario.created_at.desc()'))
