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

    return render_template('/search_customer.html', form=form)


@customer_bp.route('/search/<category>', methods=['GET', 'POST'])
def search_customer(category):
    """access page to enter customer search details"""

    form = RemoveCustomer()
    if category == 'customer_id':
        del form.first_name, form.last_name, form.pan, form.aadhaar, form.phone_num, form.email
    elif category == 'first_name':
        del form.customer_id, form.last_name, form.pan, form.aadhaar, form.phone_num, form.email
    elif category == 'last_name':
        del form.customer_id, form.first_name, form.pan, form.aadhaar, form.phone_num, form.email
    elif category == 'pan':
        del form.customer_id, form.first_name, form.last_name, form.aadhaar, form.phone_num, form.email
    elif category == 'aadhaar':
        del form.customer_id, form.first_name, form.last_name, form.pan, form.phone_num, form.email
    elif category == 'phone_num':
        del form.customer_id, form.first_name, form.last_name, form.pan, form.aadhaar, form.email
    elif category == 'email':
        del form.customer_id, form.first_name, form.last_name, form.pan, form.aadhaar, form.phone_num

    if form.validate_on_submit():
        # search customer in db
        customers = _search_customer_in_db(request.form, category)
        return render_template('/search_result.html', form=form, category=category)

    # enter customer details to search
    return render_template('/remove.html', form=form, category=category)


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


def _search_customer_in_db(form_obj, category):
    """seacrh for customer given in form object in db"""

    customers = None
    if category == 'customer_id':
        customers = db.session.query(Customer).filter(Customer.id ==
                                                      form_obj['customer_id']).all()
    elif category == 'first_name':
        customers = db.session.query(Customer).filter(Customer.id ==
                                                      form_obj['first_name']).all()
    elif category == 'last_name':
        customers = db.session.query(Customer).filter(Customer.id ==
                                                      form_obj['last_name']).all()
    elif category == 'pan':
        customers = db.session.query(Customer).filter(Customer.id ==
                                                      form_obj['pan']).all()
    elif category == 'aadhaar':
        customers = db.session.query(Customer).filter(Customer.id ==
                                                      form_obj['aadhaar']).all()
    elif category == 'email':
        customers = db.session.query(Customer).filter(Customer.id ==
                                                      form_obj['email']).all()
    elif category == 'phone':
        customers = db.session.query(Customer).filter(Customer.id ==
                                                      form_obj['phone']).all()
    return customers

