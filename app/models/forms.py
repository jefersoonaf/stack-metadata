from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo

class LoginForm(FlaskForm): 
    email = StringField("Email", validators=[DataRequired(), Email(message="O endereço de email é inválido!")], render_kw={'autofocus': True})
    password = PasswordField("Senha", validators=[DataRequired()])
    remember = BooleanField('Lembre-se de mim')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm): 
    name = StringField('Nome e Sobrenome', validators=[DataRequired()], render_kw={'autofocus': True})
    email = StringField('Email', validators=[DataRequired(), Email(message="O endereço de email é inválido!")])
    password = PasswordField('Senha', validators=[DataRequired()])
    confirm_password = PasswordField('Confirme a senha', validators=[DataRequired(), EqualTo('password', message="A confirmação de senha está incorreta!")])
    submit = SubmitField('Registre-se')

class ProfileForm(FlaskForm): 
    name = StringField("Nome e Sobrenome", validators=[DataRequired()], render_kw={'autofocus': True})
    current_password = PasswordField("Senha atual", validators=[DataRequired()])
    new_password = PasswordField("Nova senha", validators=[DataRequired()])
    confirm_new_password = PasswordField("Confirme a nova senha", validators=[DataRequired(), EqualTo('new_password', message="A confirmação de senha está incorreta!")])
    confirm_change = BooleanField('Confirma a alteração?', validators=[DataRequired()])
    submit = SubmitField('Alterar dados')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message="O endereço de email é inválido!")], render_kw={'autofocus': True})
    submit = SubmitField('Solicitar código')
    

class VerifyCodeForgotPasswordForm(FlaskForm):
    code = IntegerField('Código', validators=[DataRequired()], render_kw={'autofocus': True})
    submit = SubmitField('Verificar')
    
    
class ChangePasswordForm(FlaskForm):
    new_password = PasswordField("Nova senha", validators=[DataRequired()], render_kw={'autofocus': True})
    confirm_new_password = PasswordField("Confirme a nova senha", validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Alterar senha')