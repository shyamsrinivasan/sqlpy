from flask import render_template
from . import customer_bp
from .forms import CustomerSignup
from flask_login import login_required


@customer_bp.route('/customer/add', methods=['GET', 'POST'])
# @login_required
def add():
    """route to access customer addition form/page"""
    form = CustomerSignup()
    return render_template('/add.html', form=form)


@customer_bp.route('/customer/remove')
# @login_required
def remove():
    """route access customer removal form/page"""
    return render_template('/remove.html')


@customer_bp.route('/customer/modify')
# @login_required
def modify():
    """route to change customer details"""
    return render_template('/modify.html')



