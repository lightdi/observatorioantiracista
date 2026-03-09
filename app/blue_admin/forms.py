"""
Formulários Flask-WTF do painel administrativo.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Optional, Length


class LoginForm(FlaskForm):
    """Formulário de login."""
    username = StringField("Usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    remember = BooleanField("Lembrar-me", default=False)


class PostForm(FlaskForm):
    """Formulário de criação/edição de post."""
    titulo = StringField("Título", validators=[DataRequired(), Length(max=200)])
    slug = StringField("Slug (deixe em branco para gerar do título)", validators=[Optional(), Length(max=220)])
    categoria_slug = SelectField(
        "Categoria",
        choices=[
            ("indigenas", "Indígenas"),
            ("afro-brasileiros", "Afro-Brasileiros"),
            ("ciganos-roma", "Ciganos/Roma"),
            ("cultura-resistencia", "Cultura & Resistência"),
        ],
        validators=[DataRequired()],
    )
    resumo = StringField("Resumo (opcional)", validators=[Optional(), Length(max=500)])
    imagem_url = StringField("URL da imagem (opcional)", validators=[Optional(), Length(max=500)])
    conteudo = TextAreaField("Conteúdo", validators=[DataRequired()])
    publicado = BooleanField("Publicado", default=True)


class EscolaForm(FlaskForm):
    """Formulário para cadastro de Escola."""
    nome = StringField("Nome da Instituição", validators=[DataRequired(), Length(max=200)])
    cidade = StringField("Cidade", validators=[Optional(), Length(max=100)])
    estado = StringField("Estado (UF)", validators=[Optional(), Length(max=2)])


import flask_wtf.file as wtf_file
from wtforms import FloatField

class PraticaForm(FlaskForm):
    """Formulário para cadastro de Prática Antirracista."""
    titulo = StringField("Título da Prática", validators=[DataRequired(), Length(max=250)])
    escola_id = SelectField("Escola/Instituição", coerce=int, validators=[DataRequired()])
    categoria_slug = SelectField(
        "Categoria Temática",
        choices=[
            ("indigenas", "Indígenas"),
            ("afro-brasileiros", "Afro-Brasileiros"),
            ("ciganos-roma", "Ciganos/Roma"),
            ("cultura-resistencia", "Cultura & Resistência"),
        ],
        validators=[DataRequired()],
    )
    descricao = TextAreaField("Descrição da Prática", validators=[DataRequired()])
    endereco = StringField("Endereço Completo", validators=[Optional(), Length(max=300)])
    latitude = FloatField("Latitude", validators=[Optional()])
    longitude = FloatField("Longitude", validators=[Optional()])
    
    anexos = wtf_file.MultipleFileField("Anexos (Opcional)")


class ArtigoForm(FlaskForm):
    """Formulário para cadastro de Artigo."""
    titulo = StringField("Título do Artigo", validators=[DataRequired(), Length(max=250)])
    autor_nome = StringField("Autor(es)", validators=[DataRequired(), Length(max=150)])
    resumo = TextAreaField("Resumo", validators=[DataRequired()])
    conteudo = TextAreaField("Conteúdo", validators=[Optional()])
    publicado = BooleanField("Publicado?", default=True)


class PesquisaForm(FlaskForm):
    """Formulário para cadastro de Pesquisa."""
    titulo = StringField("Título da Pesquisa", validators=[DataRequired(), Length(max=250)])
    autores = StringField("Autor(es)/Instituição", validators=[DataRequired(), Length(max=300)])
    descricao = TextAreaField("Descrição da Pesquisa", validators=[DataRequired()])
    publicado = BooleanField("Publicado?", default=True)


class NoticiaForm(FlaskForm):
    """Formulário para cadastro de Notícia."""
    titulo = StringField("Título da Notícia", validators=[DataRequired(), Length(max=250)])
    descricao = TextAreaField("Conteúdo da Notícia", validators=[DataRequired()])
    publicado = BooleanField("Publicado?", default=True)
