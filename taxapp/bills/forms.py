from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, FloatField
from wtforms import FormField, FieldList, SubmitField
from wtforms.validators import DataRequired, Optional, Length
from .models import Items


class InvoiceItems(FlaskForm):
    """invoice items form - used with FormField and FieldList in NewInvoice"""
    # number = IntegerField('#', [DataRequired(message='Provide item number')])
    bill_item = StringField('Item Description',
                            [DataRequired(message='Please provide a description for the order item')])
    # item_price = FloatField('Price per Unit', [Optional()])
    # price = FloatField('Price per Unit', [DataRequired(message='Enter cost of one unit of item')])
    # item_quant = IntegerField('Quantity', [Optional()])
    item_cost = FloatField('Cost', [Optional()])


class NewInvoice(FlaskForm):
    """invoice entry form"""
    bill_number = StringField('Bill #', [DataRequired(message='Please provide a unique bill number'),
                                         Length(min=11,
                                                max=11,
                                                message='Bill # should be 11 characters')])
    # bill_date =
    customer_name = StringField('Customer Name',
                                [DataRequired(message='Please provide a customer name')])
    customer_id = IntegerField('ID', [Optional()])
    pan = StringField('PAN', [Optional(),
                              Length(min=10,
                                     max=10,
                                     message='PAN should be 10 characters')])
    # user_name = StringField('Created by', [Optional()])

    items = FieldList(FormField(InvoiceItems, default=lambda: Items()))

    submit = SubmitField('Add Customer')