from flask import render_template, request, flash, redirect, url_for
from . import customer_bp
from .forms import CustomerSignup, SearchCustomer, SearchCustomerCategory, ReviewCustomer
from .forms import ModifyCustomer, ModifyCustomerInfo, ModifyCustomerContact
from .forms import ModifyCustomerAddress, ModifyAllCustomer
from .models import Customer, Address, Identity, TaxInfo
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
        customer_name = new_customer_obj.set_full_name()
        # set phone number
        new_customer_obj.set_full_phone(country_code=request.form['phone_num-country_code'],
                                        phone_number=request.form['phone_num-phone_num'])
        # set added user
        new_customer_obj.set_added_user(change_type='add',
                                        username=current_user.username)

        # create identity object
        new_identity_obj = Identity(customer_name=new_customer_obj.fullname,
                                    dob=request.form['identity-dob'],
                                    pan=request.form['identity-pan'],
                                    aadhaar=request.form['identity-aadhaar'])

        # create address object
        new_address_obj = Address(customer_name=new_customer_obj.fullname,
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

        # check if customer is present in db
        if new_customer_obj.is_customer_exist():
            # get customer id for existing customer
            customer_info = db.session.query(Customer). \
                filter(Customer.fullname == customer_name).first()
            # set customer id for identity object
            new_identity_obj.set_customer_id(customer_info.id)
            # set customer id for address object
            new_address_obj.set_customer_id(customer_info.id)

            # check if customer is present in address table in db
            if new_identity_obj.is_customer_exist():
                if new_address_obj.is_customer_exist():
                    flash(message='Customer with name {}, PAN {} and address ID {} already exists'.
                          format(customer_info.fullname,
                                 customer_info.identity_info.pan,
                                 customer_info.address_info.id),
                          category='primary')
                    return redirect(url_for('customer.add'))

                # add address object to session and commit to db
                _add_table_row(new_address_obj)
                flash(message='Customer with name {} and PAN {} already exists. Address added'.
                      format(customer_info.fullname,
                             customer_info.identity_info.pan),
                      category='primary')
                return redirect(url_for('user.dashboard', username=current_user.username))

            # add identity object to session and commit to db
            _add_table_row(new_identity_obj)

            if new_address_obj.is_customer_exist():
                flash(message='Customer with name {}, PAN {} and address ID {} already exists'.
                      format(customer_info.fullname,
                             new_identity_obj.pan,
                             customer_info.address_info.id),
                      category='primary')
                return redirect(url_for('customer.add'))

            # add address object to session and commit to db
            _add_table_row(new_address_obj)
            flash(message='Customer with name {} and PAN {} already exists. Address added'.
                  format(customer_info.fullname,
                         customer_info.identity_info.pan),
                  category='primary')
            return redirect(url_for('user.dashboard', username=current_user.username))

        # add customer object to session and commit to db
        _add_table_row(new_customer_obj)
        # get customer id for new customer
        customer_info = db.session.query(Customer). \
            filter(Customer.fullname == customer_name).first()
        # set customer id for identity object
        new_identity_obj.set_customer_id(customer_info.id)
        # set customer id for address object
        new_address_obj.set_customer_id(customer_info.id)
        # add identity object to session and commit to db
        _add_table_row(new_identity_obj)
        # add address object to session and commit to db
        _add_table_row(new_address_obj)
        # get all info for newly added customer identity
        customer_info = db.session.query(Customer). \
            filter(Customer.id == customer_info.id).first()

        flash('Addition of new customer {} '
              'with ID {}, PAN {} and address ID {} successful'.
              format(customer_info.fullname,
                     customer_info.id,
                     customer_info.identity_info.pan,
                     customer_info.address_info.id),
              category='success')
        return redirect(url_for('user.dashboard', username=current_user.username))

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
    remove_form = ReviewCustomer()
    data = []
    if category == 'customerid':
        del form.first_name, form.last_name, form.identity, \
            form.phone_num, form.email
    elif category == 'firstname':
        del form.customer_id, form.last_name, form.identity, \
            form.phone_num, form.email
    elif category == 'lastname':
        del form.customer_id, form.first_name, form.identity, \
            form.phone_num, form.email
    elif category == 'pan' or category == 'aadhaar' or category == 'dob':
        del form.customer_id, form.first_name, form.last_name, form.phone_num, \
            form.email
        if category == 'pan':
            del form.identity.form.aadhaar, form.identity.form.dob
        elif category == 'aadhaar':
            del form.identity.form.pan, form.identity.form.dob
        elif category == 'dob':
            del form.identity.form.aadhaar, form.identity.form.pan
    elif category == 'phone':
        del form.customer_id, form.first_name, form.last_name, \
            form.identity, form.email
    elif category == 'email':
        del form.customer_id, form.first_name, form.last_name, \
            form.identity, form.phone_num
    elif category == 'all':
        del form.customer_id, form.first_name, form.last_name, form.identity, \
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
            data = request.form['identity-pan']
        elif category == 'aadhaar':
            data = request.form['identity-aadhaar']
        elif category == 'dob':
            data = request.form['identity-dob']
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
        return render_template('/search_result_customer.html', form=form, remove_form=remove_form,
                               category=category, result=customers)

    # enter customer details to search
    return render_template('/search_customer_category.html', form=form, category=category)


@customer_bp.route('/remove', methods=['GET', 'POST'])
def remove():
    """route to remove customer"""

    form = ReviewCustomer()
    review_form = CustomerSignup()
    review_list = []
    customer_id = ''
    if form.validate_on_submit():
        # retrieve customer with matching customer id
        customer_id = request.form['customer_id']
        review_list = db.session.query(Customer).\
            filter(Customer.id == customer_id).first()
        # review_list = db.session.query(Customer).join(Address).\
        #     filter(Customer.id == customer_id).first()
        # db.session.query(Customer, Address).filter(Customer.id == Address.customer_id).all()

        if review_list is not None:
            # customer table
            review_form.first_name.data = review_list.firstname
            review_form.last_name.data = review_list.lastname
            review_form.customer_type.data = review_list.type
            review_form.phone_num.phone_num.data = review_list.phone
            review_form.email.data = review_list.email

            # address table
            if review_list.address_info is not None:
                review_form.address.street_num.data = review_list.address_info.street_num
                review_form.address.street_name.data = review_list.address_info.street_name
                review_form.address.house_num.data = review_list.address_info.house_num
                review_form.address.locality.data = review_list.address_info.locality
                # review_form.address.locality_2.data = review_list.address_info.locality_2
                review_form.address.state.data = review_list.address_info.state
                review_form.address.city.data = review_list.address_info.city
                review_form.address.pincode.data = review_list.address_info.pin

            if review_list.identity_info is not None:
                review_form.identity.dob.data = review_list.identity_info.dob
                review_form.identity.pan.data = review_list.identity_info.pan
                review_form.identity.aadhaar.data = review_list.identity_info.aadhaar

            return render_template('/review_customer.html', form=form, result=review_list,
                                   review_form=review_form, customer_id=customer_id)
        else:
            flash('Customer with ID {} does not exist'.format(customer_id), category='error')
            return redirect(url_for('customer.search'))

    return render_template('/review_customer.html', form=form, result=review_list,
                           review_form=review_form, customer_id=customer_id)


@customer_bp.route('/remove/<customer_id>', methods=['GET'])
def remove_customer(customer_id):
    """remove specific customer with customer_id from db"""
    # run delete row query on customer/address/taxinfo
    db.session.query(Address).filter(Address.customer_id == customer_id).delete()
    db.session.commit()
    db.session.query(Identity).filter(Identity.customer_id == customer_id).delete()
    db.session.commit()
    db.session.query(Customer).filter(Customer.id == customer_id).delete()
    db.session.commit()

    flash(message='customer with ID {} removed'.format(customer_id), category='success')
    return redirect(url_for('customer.remove'))


@customer_bp.route('/modify', methods=['GET', 'POST'])
# @login_required
def modify():
    """route to change customer details"""

    form = ModifyCustomer()
    if form.validate_on_submit():
        customer_id = request.form['customer_id']
        category = request.form['modify_by']
        return redirect(url_for('customer.modify_customer', category=category,
                                customer_id=customer_id))
    return render_template('/modify_customer.html', form=form, category='')


@customer_bp.route('/modify/<category>/<customer_id>', methods=['GET'])
def modify_customer(category, customer_id):
    """modify different types of info for customer"""

    review_list = db.session.query(Customer). \
        filter(Customer.id == customer_id).first()

    if category == 'basic_info':
        form = ModifyCustomerInfo()
        if review_list is not None:
            form.first_name.data = review_list.firstname
            form.last_name.data = review_list.lastname
            form.customer_type.data = review_list.type

            if review_list.identity_info is not None:
                form.identity.dob.data = review_list.identity_info.dob
                form.identity.pan.data = review_list.identity_info.pan
                form.identity.aadhaar.data = review_list.identity_info.aadhaar

    elif category == 'address':
        address_list = db.session.query(Address).\
            filter(Address.customer_id == customer_id).first()
        form = ModifyCustomerAddress()

        if address_list is not None:
            form.address.street_num.data = address_list.street_num
            form.address.street_name.data = address_list.street_name
            form.address.house_num.data = address_list.house_num
            form.address.locality.data = address_list.locality
            # form.address.locality_2.data = address_list.locality_2
            form.address.state.data = address_list.state
            form.address.city.data = address_list.city
            form.address.pincode.data = address_list.pin

    elif category == 'contact':
        form = ModifyCustomerContact()

        if review_list is not None:
            form.phone_num.phone_num.data = review_list.phone
            form.email.data = review_list.email
    # elif category == 'billing':
    #     pass
    elif category == 'all':
        form = ModifyAllCustomer()

        if review_list is not None:
            form.first_name.data = review_list.firstname
            form.last_name.data = review_list.lastname
            form.customer_type.data = review_list.type
            form.phone_num.phone_num.data = review_list.phone
            form.email.data = review_list.email

            if review_list.identity_info is not None:
                form.identity.dob.data = review_list.identity_info.dob
                form.identity.pan.data = review_list.identity_info.pan
                form.identity.aadhaar.data = review_list.identity_info.aadhaar

            if review_list.address_info is not None:
                form.address.street_num.data = review_list.address_info.street_num
                form.address.street_name.data = review_list.address_info.street_name
                form.address.house_num.data = review_list.address_info.house_num
                form.address.locality.data = review_list.address_info.locality
                # form.address.locality_2.data = review_list.address_info.locality_2
                form.address.state.data = review_list.address_info.state
                form.address.city.data = review_list.address_info.city
                form.address.pincode.data = review_list.address_info.pin

    else:
        form = ModifyCustomer()

    return render_template('/modify_customer.html', category=category,
                           form=form, customer_id=customer_id, result=review_list)


@customer_bp.route('/modify/<category>/<customer_id>', methods=['POST'])
def modify_customer_db(category, customer_id):
    """change customer info in db"""

    existing_entry = db.session.query(Customer). \
        filter(Customer.id == customer_id).first()

    if category == 'basic_info':
        form = ModifyCustomerInfo()
    elif category == 'address':
        form = ModifyCustomerAddress()
    elif category == 'contact':
        form = ModifyCustomerContact()
    # elif category == 'billing':
    #     pass
    elif category == 'all':
        form = ModifyAllCustomer()
    else:
        form = ModifyCustomer()

    if form.validate_on_submit():
        # check which values are different and update relevant customer table
        return 'Customer modified'


def _add_table_row(table_class_obj):
    """take any table ORM class object and
    add as row to corresponding table"""

    db.session.add(table_class_obj)
    db.session.commit()
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
        customers = db.session.query(Customer).\
            join(Identity).filter(Identity.pan == value).all()
    elif category == 'aadhaar':
        customers = db.session.query(Customer). \
            join(Identity).filter(Identity.aadhaar == value).all()
    elif category == 'dob':
        customers = db.session.query(Customer). \
            join(Identity).filter(Identity.dob == value).all()
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

