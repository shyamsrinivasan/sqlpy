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
        new_customer_obj.set_full_phone(country_code=request.form['phone_num-country_code'],
                                        phone_number=request.form['phone_num-phone_num'])
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


@customer_bp.route('/search', methods=['GET', 'POST'])
# @login_required
def search():
    """route access first customer removal form/page (choose search category)"""
    # go to search category page -> details page -> remove page
    form = SearchCustomer()
    if form.validate_on_submit():  # if request.method == 'POST':
        return redirect(url_for('customer.search_category', category=request.form['search_by']))

    return render_template('/search_customer.html', form=form)


@customer_bp.route('/search/<category>', methods=['GET', 'POST'])
def search_category(category):
    """access page to enter customer search details"""

    form = RemoveCustomer()
    data = []
    if category == 'customerid':
        del form.first_name, form.last_name, form.pan, form.aadhaar, form.phone_num, form.email
    elif category == 'firstname':
        del form.customer_id, form.last_name, form.pan, form.aadhaar, form.phone_num, form.email
    elif category == 'lastname':
        del form.customer_id, form.first_name, form.pan, form.aadhaar, form.phone_num, form.email
    elif category == 'pan':
        del form.customer_id, form.first_name, form.last_name, form.aadhaar, form.phone_num, form.email
    elif category == 'aadhaar':
        del form.customer_id, form.first_name, form.last_name, form.pan, form.phone_num, form.email
    elif category == 'phone':
        del form.customer_id, form.first_name, form.last_name, form.pan, form.aadhaar, form.email
    elif category == 'email':
        del form.customer_id, form.first_name, form.last_name, form.pan, form.aadhaar, form.phone_num

    if form.validate_on_submit():
        # search customer in db
        if category == 'customerid':
            data = request.form['customer_id']
        elif category == 'firstname':
            data = request.form['first_name']
        elif category == 'lastname':
            data = request.form['last_name']
        elif category == 'pan':
            data = request.form['pan']
        elif category == 'aadhaar':
            data = request.form['aadhaar']
        elif category == 'phone':
            data = request.form['phone_num-country_code'] + \
                   request.form['phone_num-phone_num']
        elif category == 'email':
            data = request.form['email']
        else:
            data = []

        customers = _search_customer_in_db(data, category)
        if not customers:
            flash(message='no customers found with given details', category='error')
        return render_template('/search_result.html', form=form,
                               category=category, result=customers)

    # enter customer details to search
    return render_template('/search.html', form=form, category=category)


@customer_bp.route('/remove')
def remove():
    """route to remove customer"""
    return render_template('/remove.html')


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

    # customers = None
    if category == 'customerid':
        customers = db.session.query(Customer).filter(Customer.id == form_obj).all()
    elif category == 'firstname':
        customers = db.session.query(Customer).filter(Customer.firstname ==
                                                      form_obj).all()
    elif category == 'lastname':
        customers = db.session.query(Customer).filter(Customer.lastname ==
                                                      form_obj).all()
    elif category == 'pan':
        customers = db.session.query(Customer).filter(Customer.pan ==
                                                      form_obj).all()
    elif category == 'aadhaar':
        customers = db.session.query(Customer).filter(Customer.aadhaar ==
                                                      form_obj).all()
    elif category == 'email':
        customers = db.session.query(Customer).filter(Customer.email ==
                                                      form_obj).all()
    elif category == 'phone':
        # phone_number = form_obj['phone_num-country_code'] + \
        #                form_obj['phone_num-phone_num']
        customers = db.session.query(Customer).filter(Customer.phone ==
                                                      form_obj).all()
    else:
        customers = []
    return customers


