from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms import HiddenField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    """Form to sign in to application"""

    username = StringField('Username', [DataRequired(message='Please enter a username')])
    password = PasswordField('Password', [DataRequired(message='Please enter a password')])
    next = HiddenField('Next Value')

    submit = SubmitField('Sign in')


class ContactForm(FlaskForm):
    """Form for contacting creator"""

    name = StringField('Name', [DataRequired()])
    email = EmailField('Email', [Email(message='Not a valid email address'), DataRequired()])
    message = TextAreaField('Message', [DataRequired(), Length(min=4, message='Your message is too short')])

    recaptcha = RecaptchaField()
    submit = SubmitField('Send Message')
