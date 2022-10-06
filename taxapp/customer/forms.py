from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, DateField, SelectField
from wtforms import SubmitField
from wtforms.validators import DataRequired, Email, Optional
from wtforms.validators import ValidationError


def phone_num(minimum=-1, maximum=-1):
    message = 'Must be between %d (without +country code) and %d (with +country code) characters long' % (minimum, maximum)

    def _phone_num(form, field):
        l = field.data and len(field.data) or 0
        if l < minimum or maximum != -1 and l > maximum:
            raise ValidationError(message)
    return _phone_num


class CustomerSignup(FlaskForm):
    """form to add customer to database"""

    first_name = StringField('First Name', [DataRequired(message='Please provide a first name')])
    last_name = StringField('Last Name', [DataRequired(message='Please provide a last name')])
    dob = DateField('Date of Birth', [DataRequired()])
    customer_type = SelectField('Customer Type', [DataRequired()], choices=[('personal', 'individual'),
                                                                            ('commercial', 'business')])
    country_code = SelectField('Code', [Optional()], choices=[('india', '+91'),
                                                              ('usa', '+1')])
    phone = StringField('Phone', [Optional(), phone_num(minimum=10, maximum=14)])
    email = EmailField('Email', [Email(message='Not a valid email address'), Optional()])

    # recaptcha = RecaptchaField()
    submit = SubmitField('Add Customer')
