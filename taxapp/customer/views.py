from flask import render_template, request, flash, redirect, url_for
from . import customer_bp
from .forms import CustomerSignup, SearchCustomer, SearchCustomerCategory, RemoveCustomer
from .models import Customer, Address, TaxInfo
from taxapp import db
from flask_login import login_required, current_user


@customer_bp.route('/add', methods=['GET', 'POST'])
# @login_required
def add():
    """route to access customer addition form/page"""
    form = CustomerSignup()
    if form.validate_on_submit():
        # create customer object
        new_customer_obj = Customer(firstname=request.form['first_name'],
                                    lastname=request.form['last_name'],
                                    type=request.form['customer_type'],
                                    email=request.form['email'])
        # set full name-
        fullname = new_customer_obj.set_full_name()
        customer_name = new_customer_obj.fullname

        # set phone number
        new_customer_obj.set_full_phone(country_code=request.form['phone_num-country_code'],
                                        phone_number=request.form['phone_num-phone_num'])
        # set added user
        new_customer_obj.set_added_user(change_type='add',
                                        username=current_user.username)

        # check if customer is present in db
        customer_not_present = True
        customer_info = db.session.query(Customer).filter(Customer.fullname == customer_name).first()
        if customer_info:
            customer_not_present = False

        if customer_not_present:
            # add user object to session and commit to db
            db.session.add(new_customer_obj)
            db.session.commit()
            # get customer id for newly added customer
            customer_info = db.session.query(Customer).filter(Customer.fullname == fullname).first()
            flash('Addition of new customer {} successful'.format(customer_name),
                  category='success')

        # create address object
        new_address_obj = Address(customer_id=customer_info.id,
                                  customer_name=customer_info.fullname,
                                  type=request.form['address-house_type'],
                                  street_num=request.form['address-street_num'],
                                  street_name=request.form['address-street_name'],
                                  house_num=request.form['address-house_num'],
                                  locality=request.form['address-locality'],
                                  city=request.form['address-city'],
                                  state=request.form['address-state'],
                                  pin=request.form['address-pincode'])
        # set added user
        new_address_obj.set_added_user(change_type='add',
                                       username=current_user.username)

        # check if customer address is present in db
        address_not_present = True
        address_info = db.session.query(Address).filter(Address.customer_id == customer_info.id).first()
        if address_info:
            address_not_present = False

        if address_not_present:
            # add address object to session and commit to db
            db.session.add(new_address_obj)
            db.session.commit()

        if customer_not_present and address_not_present:
            flash('Addition of new customer {} and address successful'.format(customer_name),
                  category='success')
        elif not customer_not_present and address_not_present:
            flash('Customer {} already exists. Address addition successful'.format(customer_name),
                  category='success')
        else:
            flash('Customer {} and address already present. No additions made.'.format(customer_name),
                  category='info')

        return redirect(url_for('admin.dashboard', username=current_user.username))

    return render_template('/add.html', form=form)


@customer_bp.route('/search', methods=['GET', 'POST'])
# @login_required
def search():
    """route access first customer removal form/page (choose search category)"""
    # go to search category page -> details page -> remove page
    form = SearchCustomerCategory()
    if form.validate_on_submit():  # if request.method == 'POST':
        return redirect(url_for('customer.search_category', category=request.form['search_by']))

    return render_template('/search_customer.html', form=form)


@customer_bp.route('/search/<category>', methods=['GET', 'POST'])
def search_category(category):
    """access page to enter customer search details"""

    form = SearchCustomer()
    remove_form = RemoveCustomer()
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
    elif category == 'all':
        del form.customer_id, form.first_name, form.last_name, form.pan, form.aadhaar, \
            form.phone_num, form.email

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
        elif category == 'all':
            data = request.form
        else:
            data = []

        customers = _search_customer_in_db(data, category)
        if not customers:
            flash(message='no customers found with given details', category='error')
        # return redirect(url_for('customer.search_result',
        #                         category=category, result=customers))
        return render_template('/search_result.html', form=form, remove_form=remove_form,
                               category=category, result=customers)

    # enter customer details to search
    return render_template('/search.html', form=form, category=category)


@customer_bp.route('/remove', methods=['GET', 'POST'])
def remove():
    """route to remove customer"""

    form = RemoveCustomer()
    review_form = CustomerSignup()
    review_list = []
    customer_id = ''
    if form.validate_on_submit():
        # retrieve customer with matching customer id
        customer_id = request.form['customer_id']
        review_list = db.session.query(Customer).\
            filter(Customer.id == customer_id).first()

        if review_list:
            review_form.first_name.data = review_list.firstname
            review_form.last_name.data = review_list.lastname
            review_form.customer_type.data = review_list.type
            # review_form.dob.data = review_list.dob
            # review_form.pan.data = review_list.pan
            # review_form.aadhaar.data = review_list.aadhaar
            # review_form.customer_type.data = review_list.type
            # review_form.phone_num.phone_num.data = review_list.phone
            review_form.email.data = review_list.email

        # return render_template('/remove.html', form=form, result=review_list)
    return render_template('/remove.html', form=form, result=review_list,
                           review_form=review_form, customer_id=customer_id)


@customer_bp.route('/remove/<customer_id>', methods=['GET'])
def remove_customer(customer_id):
    """remove specific customer with customer_id from db"""
    # run delete row query on customer/address/taxinfo
    db.session.query(Address).filter(Address.customer_id == customer_id).delete()
    db.session.commit()
    # db.session.query(TaxInfo).filter(TaxInfo.customer_id == customer_id).delete()
    # db.session.commit()
    db.session.query(Customer).filter(Customer.id == customer_id).delete()
    db.session.commit()

    flash(message='customer with ID {} removed'.format(customer_id), category='success')
    return redirect(url_for('customer.remove'))


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


def _search_customer_in_db(value, category):
    """seacrh for customer given in form object in db"""

    # customers = None
    if category == 'customerid':
        customers = db.session.query(Customer).filter(Customer.id == value).all()
    elif category == 'firstname':
        customers = db.session.query(Customer).filter(Customer.firstname ==
                                                      value).all()
    elif category == 'lastname':
        customers = db.session.query(Customer).filter(Customer.lastname ==
                                                      value).all()
    elif category == 'fullname':
        customers = db.session.query(Customer).filter(Customer.fullname ==
                                                      value).all()
    elif category == 'pan':
        customers = db.session.query(Customer).filter(Customer.pan ==
                                                      value).all()
    elif category == 'aadhaar':
        customers = db.session.query(Customer).filter(Customer.aadhaar ==
                                                      value).all()
    elif category == 'email':
        customers = db.session.query(Customer).filter(Customer.email ==
                                                      value).all()
    elif category == 'phone':
        # phone_number = form_obj['phone_num-country_code'] + \
        #                form_obj['phone_num-phone_num']
        customers = db.session.query(Customer).filter(Customer.phone ==
                                                      value).all()
    elif category == 'all':
        customers = db.session.query(Customer).all()
    else:
        customers = []
    return customers


