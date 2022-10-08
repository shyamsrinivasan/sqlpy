from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms import HiddenField, EmailField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length
from wtforms.validators import Optional, ValidationError, EqualTo


class LoginForm(FlaskForm):
    """Form to sign in to application"""

    username = StringField('Username', [DataRequired(message='Please enter a username')])
    password = PasswordField('Password', [DataRequired(message='Please enter a password')])
    next = HiddenField('Next Value')

    submit = SubmitField('Sign in')


def phone_num(minimum=-1, maximum=-1):
    message = 'Must be between %d (without +country code) and %d (with +country code) characters long' % (minimum, maximum)

    def _phone_num(form, field):
        l = field.data and len(field.data) or 0
        if l < minimum or maximum != -1 and l > maximum:
            raise ValidationError(message)

    return _phone_num


class SignupForm(FlaskForm):
    """Form to signup as user in application"""

    # basic details
    first_name = StringField('First Name', [DataRequired(message='Please provide your first name')])
    last_name = StringField('Last Name', [DataRequired(message='Please provide your last name')])
    # dob = DateField('Date of Birth', [DataRequired()])
    email = EmailField('Email', [Email(message='Not a valid email address'), Optional()])
    country_code = SelectField('Code', [Optional()], choices=[('india', '+91'),
                                                              ('usa', '+1')])
    phone = StringField('Phone', [Optional(), phone_num(minimum=10, maximum=14)])

    # login details
    username = StringField('Username', [DataRequired(),
                                        Length(min=6,
                                               message='Your username should be minimum 6 characters')])
    password = PasswordField('Password', [DataRequired(message='Please enter a password'),
                                          Length(min=8,
                                                 message='Password should be at least 8 characters')])
    confirm_pass = PasswordField('ConfirmPassword', [EqualTo('password',
                                                             message='Passwords must match')])

    # specific details
    # employee_type = SelectField('Employee Type', [DataRequired()], choices=[('Administrator', 'admin'),
    #                                                                         ('User', 'user'),
    #                                                                         ('Hybrid', 'hybrid')])
    # recaptcha = RecaptchaField()
    submit = SubmitField('Create User')


class RemoveUser(FlaskForm):
    """form to remove user from db"""

    user_id = StringField('User ID', [Optional()])
    first_name = StringField('First Name', [Optional()])
    last_name = StringField('Last Name', [Optional()])
    username = StringField('Username', [Optional(),
                                        Length(min=6,
                                               message='Your username should be minimum 6 characters')])


class ContactForm(FlaskForm):
    """Form for contacting creator"""

    name = StringField('Name', [DataRequired()])
    email = EmailField('Email', [Email(message='Not a valid email address'), DataRequired()])
    message = TextAreaField('Message', [DataRequired(), Length(min=4, message='Your message is too short')])

    recaptcha = RecaptchaField()
    submit = SubmitField('Send Message')
