from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, DateField, SelectField
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Optional, Length
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

    # personal details
    first_name = StringField('First Name', [DataRequired(message='Please provide a first name')])
    last_name = StringField('Last Name', [DataRequired(message='Please provide a last name')])
    customer_type = SelectField('Customer Type', [DataRequired()], choices=[('personal', 'individual'),
                                                                            ('commercial', 'business')])
    country_code = SelectField('Code', [Optional()], choices=[('india', '+91'),
                                                              ('usa', '+1')])
    phone = StringField('Phone', [Optional(), phone_num(minimum=10, maximum=14)])
    email = EmailField('Email', [Email(message='Not a valid email address'), Optional()])

    # id details
    dob = DateField('Date of Birth', [DataRequired(message='Date of birth is required')])
    pan = StringField('PAN', [DataRequired('Please provide customer PAN'),
                              Length(min=10, max=10,
                                     message='PAN should be 10 characters')
                              ])
    aadhaar = StringField('Aadhaar', [Optional(),
                                      Length(min=12, max=12,
                                             message='Aadhaar should to 12 digits')])

    # address details
    street_num = StringField('Street Number', [DataRequired('Street number required')])
    house_num = StringField('House/Unit Number', [Optional()])
    street_name = StringField('Street Name', [DataRequired('Please provide street name')])
    locality = StringField('Area/Locality', [Optional()])
    locality_2 = StringField('Area/Locality 2', [Optional()])
    city = StringField('City', [DataRequired('City is required')])
    state = SelectField('State', [DataRequired()], choices=[('tn', 'Tanilnadu'),
                                                            ('ka', 'Karnataka'),
                                                            ('kl', 'Kerala')])
    pincode = StringField('PIN', [DataRequired('Please provide a pin/postal code'),
                                  Length(min=6, max=6,
                                         message='PIN should be 6 characters long')])

    # recaptcha = RecaptchaField()
    submit = SubmitField('Add Customer')


class RemoveCustomer(FlaskForm):
    """form to remove customer from db"""

    customer_id = StringField('Customer Number', [Optional()])
    first_name = StringField('First Name', [Optional()])
    last_name = StringField('Last Name', [Optional()])
    pan = StringField('PAN', [Optional(),
                              Length(min=10, max=10,
                                     message='PAN should be 10 characters')
                              ])
    aadhaar = StringField('Aadhaar', [Optional(),
                                      Length(min=12, max=12,
                                             message='Aadhaar should to 12 digits')
                                      ])
    phone = StringField('Phone', [Optional(), phone_num(minimum=10, maximum=14)])
    email = EmailField('Email', [Email(message='Not a valid email address'), Optional()])
