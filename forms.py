from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    nome_completo = StringField('Nome Completo', 
                                validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', 
                          validators=[DataRequired(), Length(min=6, message='A senha deve ter pelo menos 6 caracteres.')])
    confirmar_senha = PasswordField('Confirmar Senha', 
                                    validators=[DataRequired(), EqualTo('senha', message='As senhas devem ser iguais.')])
    submit = SubmitField('Criar Conta')

class LoginForm(FlaskForm):
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                             validators=[DataRequired()])
    submit = SubmitField('Sign In')