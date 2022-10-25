from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, DateField, SelectField
from wtforms import SubmitField, IntegerField, FormField, RadioField
from wtforms.validators import DataRequired, Email, Optional, Length
from wtforms.validators import ValidationError


def phone_num(minimum=-1, maximum=-1):
    message = 'Must be between %d (without +country code) and %d (with +country code) characters long' % (minimum, maximum)

    def _phone_num(form, field):
        l = field.data and len(field.data) or 0
        if l < minimum or maximum != -1 and l > maximum:
            raise ValidationError(message)
    return _phone_num


class PhoneNumber(FlaskForm):
    """phone number form for use in FormFields and FieldList"""
    country_code = SelectField('Country Code', [Optional()], choices=[('+91', 'India'),
                                                              ('+1', 'USA')])
    phone_num = StringField('Phone Number', [Optional(), Length(min=10, max=10)])


class Address(FlaskForm):
    """address form class to be used with FormFields"""

    house_type = SelectField('Type', [DataRequired()], choices=[('house', 'House'),
                                                                ('apartment', 'Apartment'),
                                                                ('single_bus', 'Single Store'),
                                                                ('complex_bus', 'Complex Store')])
    street_num = StringField('Street #', [DataRequired('Street number required')])
    house_num = StringField('House/Unit #', [Optional()])
    street_name = StringField('Street Name', [DataRequired('Please provide street name')])
    locality = StringField('Area/Locality', [Optional()])
    locality_2 = StringField('Area/Locality 2', [Optional()])
    state = SelectField('State', [DataRequired()], choices=[('TN', 'Tamilnadu'),
                                                            ('KA', 'Karnataka'),
                                                            ('KL', 'Kerala')])
    city = StringField('City', [DataRequired('City is required')])
    pincode = StringField('PIN', [DataRequired('Please provide a pin/postal code'),
                                  Length(min=6, max=6,
                                         message='PIN should be 6 characters long')])


class CustomerSignup(FlaskForm):
    """form to add customer to database"""

    # personal details
    first_name = StringField('First Name', [DataRequired(message='Please provide a first name')])
    last_name = StringField('Last Name', [DataRequired(message='Please provide a last name')])
    customer_type = SelectField('Customer Type', [DataRequired()], choices=[('personal', 'individual'),
                                                                            ('commercial', 'business')])
    phone_num = FormField(PhoneNumber)
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
    address = FormField(Address)

    # recaptcha = RecaptchaField()
    submit = SubmitField('Add Customer')


class SearchCustomerCategory(FlaskForm):
    """form to search for customer - search categories only"""
    search_by = RadioField('Search Using', [DataRequired()], choices=[('customerid', 'Customer ID'),
                                                                      ('firstname', 'First Name'),
                                                                      ('lastname', 'Last Name'),
                                                                      ('pan', 'PAN'),
                                                                      ('aadhaar', 'Aadhaar'),
                                                                      ('phone', 'Phone #'),
                                                                      ('email', 'Email'),
                                                                      ('all', 'Display All')],
                           default='customerid')
    submit = SubmitField('Enter Customer Details')


class SearchCustomer(FlaskForm):
    """form to search customer from db - input form for details to search"""
    customer_id = StringField('Customer ID',
                              [DataRequired(message='Please provide a customer # to search for')])
    first_name = StringField('First Name',
                             [DataRequired(message='Please provide a first name to search')])
    last_name = StringField('Last Name',
                            [DataRequired(message='Please provide a last name to search')])
    pan = StringField('PAN', [DataRequired(message='Please provide a PAN to search'),
                              Length(min=10, max=10,
                                     message='PAN should be 10 characters')
                              ])
    aadhaar = StringField('Aadhaar', [DataRequired(message='Please provide a aadhaar number to search'),
                                      Length(min=12, max=12,
                                             message='Aadhaar should to 12 digits')
                                      ])
    # country_code = SelectField('Code', [Optional()], choices=[('+91', 'India'),
    #                                                           ('+1', 'USA')])
    # phone = StringField('Phone', [Optional(), phone_num(minimum=10, maximum=14)])
    phone_num = FormField(PhoneNumber)
    email = EmailField('Email', [Email(message='Not a valid email address'),
                                 DataRequired(message='Please provide a email to search')])

    # submit_new_category = RadioField('Choose Different Category', [Optional()],
    #                                  choices=[('new_choice', 'Choose Different Category')])
    submit = SubmitField('Search Customer')


class RemoveCustomer(FlaskForm):
    """form to enter id or pan to remove customer"""

    customer_id = StringField('Customer ID',
                              [DataRequired(message='Please provide a customer # to search for')])
    # pan = StringField('PAN', [DataRequired(message='Please provide a PAN to search'),
    #                           Length(min=10, max=10,
    #                                  message='PAN should be 10 characters')
    #                           ])
    submit = SubmitField('Review customer details')

