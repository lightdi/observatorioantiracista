from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class RegisterForm(FlaskForm):
    """Formulário de cadastro de usuário comum."""
    username = StringField("Nome de Usuário", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirmar Senha", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Cadastrar")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Nome de usuário já está em uso.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Endereço de e-mail já está registrado.")

class PublicLoginForm(FlaskForm):
    """Formulário de login unificado (público)."""
    username = StringField("Usuário ou Email", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    remember = BooleanField("Lembrar-me")
    submit = SubmitField("Entrar")
