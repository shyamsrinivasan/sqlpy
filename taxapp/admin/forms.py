from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    """Form to sign in to application"""

    username = StringField('Username', [DataRequired(message='Please enter a username')])
    password = PasswordField('Password', [DataRequired(message='Please enter a password')])

    submit = SubmitField('Sign in')
