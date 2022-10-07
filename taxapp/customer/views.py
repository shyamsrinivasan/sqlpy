from flask import render_template, request, flash
from . import customer_bp
from .forms import CustomerSignup
from flask_login import login_required


@customer_bp.route('/customer/add', methods=['GET', 'POST'])
# @login_required
def add():
    """route to access customer addition form/page"""
    form = CustomerSignup()
    if form.validate_on_submit():
        _add_customer(request.form)
        customer_name = 'customer name'
        flash('Addition of new customer {} successful'.format(customer_name))
        return 'Customer added successfully'
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


def _add_customer(form_obj):
    """take user details in form_obj to create Customer object and
    add as row to customer table"""
    # generate user object
    # new_user_obj = User(firstname=form_obj['first_name'], lastname=form_obj['last_name'],
    #                     email=form_obj['email'], phone=form_obj['phone'],
    #                     username=form_obj['username'])
    # # add hashed password to db
    # new_user_obj.set_password(form_obj['password'])
    # db.session.add(new_user_obj)
    # db.session.commit()
    return None


