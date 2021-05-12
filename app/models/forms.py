from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm): 
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])

class RegisterForm(FlaskForm): 
    name = StringField("name", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    repeat_password = PasswordField("repeat_password", validators=[DataRequired()])

class ProfileForm(FlaskForm): 
    name = StringField("name", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired()])
    current_password = PasswordField("current_password", validators=[DataRequired()])
    new_password = PasswordField("new_password", validators=[DataRequired()])
    repeat_new_password = PasswordField("repeat_new_password", validators=[DataRequired()])