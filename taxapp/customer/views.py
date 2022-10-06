from flask import render_template
from . import customer_bp
from .forms import CustomerSignup
from flask_login import login_required


@customer_bp.route('/add_customers', methods=['GET', 'POST'])
# @login_required
def add_customer():
    """route to access customer addition form/page"""
    form = CustomerSignup()
    return render_template('/add.html', form=form)


@customer_bp.route('/remove_customer')
# @login_required
def remove_customer():
    """route access customer removal form/page"""
    return render_template('/remove.html')


@customer_bp.route('/modify_customer')
# @login_required
def modify_customer():
    """route to change customer details"""
    return render_template('/modify.html')



