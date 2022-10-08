from flask import render_template, request, flash
from . import customer_bp
from .forms import CustomerSignup
from .models import Customer
from taxapp import db
from flask_login import login_required


@customer_bp.route('/customer/add', methods=['GET', 'POST'])
# @login_required
def add():
    """route to access customer addition form/page"""
    form = CustomerSignup()
    if form.validate_on_submit():
        new_customer_obj = Customer(firstname=request.form['first_name'],
                                    lastname=request.form['last_name'],
                                    type=request.form['customer_type'],
                                    email=request.form['email'])
        # set full name-
        new_customer_obj.set_full_name()
        customer_name = new_customer_obj.fullname

        # set phone number
        new_customer_obj.set_full_phone(country_code=request.form['country_code'],
                                        phone_number=request.form['phone'])

        # add user object to session and commit to db
        db.session.add(new_customer_obj)
        db.session.commit()

        flash('Addition of new customer {} successful'.format(customer_name))
        return 'Customer added successfully'
        # return redirect(url_for('admin.dashboard', username=current_user.username))
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

    # # add hashed password to db
    # new_user_obj.set_password(form_obj['password'])
    # db.session.add(new_user_obj)
    # db.session.commit()
    return None


