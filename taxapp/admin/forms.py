from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField
from wtforms import EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class ContactForm(FlaskForm):
    """Form for contacting creator"""

    name = StringField('Name', [DataRequired()])
    email = EmailField('Email', [Email(message='Not a valid email address'), DataRequired()])
    message = TextAreaField('Message', [DataRequired(), Length(min=4, message='Your message is too short')])

    recaptcha = RecaptchaField()
    submit = SubmitField('Send Message')
