from flask import render_template, request, flash, redirect, url_for
from . import customer_bp
from .forms import CustomerSignup, RemoveCustomer, SearchCustomer
from .models import Customer
from taxapp import db
from flask_login import login_required, current_user


@customer_bp.route('/add', methods=['GET', 'POST'])
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
        # set added user
        new_customer_obj.set_added_user(change_type='add',
                                        username=current_user.username)

        # add user object to session and commit to db
        db.session.add(new_customer_obj)
        db.session.commit()

        flash('Addition of new customer {} successful'.format(customer_name),
              category='success')
        # return 'Customer added successfully'
        return redirect(url_for('admin.dashboard', username=current_user.username))
    return render_template('/add.html', form=form)


@customer_bp.route('/remove', methods=['GET', 'POST'])
# @login_required
def remove():
    """route access first customer removal form/page (choose search category)"""
    # go to search category page -> details page -> remove page
    form = SearchCustomer()
    if form.validate_on_submit():  # if request.method == 'POST':
        return redirect(url_for('customer.search_customer', category=request.form['search_by']))

    return render_template('/remove_1.html', form=form)


@customer_bp.route('/search/<category>', methods=['GET', 'POST'])
def search_customer(category):
    """access page to enter customer search details"""
    details_form = RemoveCustomer()
    # enter customer details to search
    # customers = search_customer(request.form)
    return render_template('/find_customer.html', form=details_form)


@customer_bp.route('/modify')
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


def search_customer(form_obj):
    """seacrh for customer given in form object in db"""
    # form_obj.customer_id
    customers = db.session.query(Customer).all()
    return customers


