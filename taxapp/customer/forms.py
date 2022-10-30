from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, DateField, SelectField
from wtforms import SubmitField, SelectMultipleField, FormField, RadioField
from wtforms.validators import DataRequired, Email, Optional, Length
from wtforms.validators import ValidationError
from wtforms.widgets import html_params


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


class CustomerID(FlaskForm):
    """form to encapsulate customer id details"""

    dob = DateField('Date of Birth', [DataRequired(message='Date of birth is required')])
    pan = StringField('PAN', [DataRequired('Please provide customer PAN'),
                              Length(min=10, max=10,
                                     message='PAN should be 10 characters')
                              ])
    aadhaar = StringField('Aadhaar', [Optional(),
                                      Length(min=12, max=12,
                                             message='Aadhaar should to 12 digits')])


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
    identity = FormField(CustomerID)

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
    identity = FormField(CustomerID)
    phone_num = FormField(PhoneNumber)
    email = EmailField('Email', [Email(message='Not a valid email address'),
                                 DataRequired(message='Please provide a email to search')])
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


def select_multi_checkbox(field, ul_class='', **kwargs):
    kwargs.setdefault('type', 'checkbox')
    field_id = kwargs.pop('id', field.id)
    html = [u'<ul %s>' % html_params(id=field_id, class_=ul_class)]
    for value, label, checked in field.iter_choices():
        choice_id = u'%s-%s' % (field_id, value)
        options = dict(kwargs, name=field.name, value=value, id=choice_id)
        if checked:
            options['checked'] = 'checked'
        html.append(u'<li><input %s /> ' % html_params(**options))
        html.append(u'<label for="%s">%s</label></li>' % (field_id, label))
    html.append(u'</ul>')
    return u''.join(html)


class ModifyCustomerCategory(FlaskForm):
    """different customer form fields to be selected for modification"""

    search_by = SelectMultipleField('Search Using', [DataRequired()],
                                    choices=[('firstname', 'First Name'),
                                             ('lastname', 'Last Name'),
                                             ('phone', 'Phone #'),
                                             ('email', 'Email'),
                                             ('dob', 'Date of Birth'),
                                             ('pan', 'PAN'),
                                             ('aadhaar', 'Aadhaar'),
                                             ('address', 'Address')],
                                    default='email', widget=select_multi_checkbox)
    submit = SubmitField('Enter Customer Details')





