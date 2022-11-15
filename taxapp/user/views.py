from flask import render_template, request, redirect, url_for, flash
from . import user_bp
from .forms import LoginForm, SearchUserCategory, SearchUser, RemoveUser, SignupForm
from .forms import ChangePassword
from .models import User
from taxapp import db, flask_bcrypt
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@user_bp.route('/signup', methods=['GET', 'POST'])
@login_required
def signup():
    """take user details in form to create User object and
        add as row to user table"""
    form = SignupForm()
    if form.validate_on_submit():
        # process sign-up information using func into db add info to db here
        # generate user object
        phone_number = request.form['phone_num-country_code'] + \
                       request.form['phone_num-phone_num']
        new_user_obj = User(firstname=request.form['first_name'],
                            lastname=request.form['last_name'],
                            email=request.form['email'],
                            phone=phone_number,
                            username=request.form['username'])
        # add hashed password to db, full name and added_by
        new_user_obj.set_password(request.form['password'])
        new_user_obj.set_full_name()
        new_user_obj.set_added_user(current_user.username)

        # check if user with firstname/lastname exists and redirect to enter data again
        if new_user_obj.is_user_exist():
            flash(message='User {} already exists'.format(new_user_obj.fullname),
                  category='primary')
            return redirect(url_for('user.signup'))

        # check if user with username exists and redirect to enter data again
        if new_user_obj.is_username_exist():
            flash(message='Username {} already exist. '
                          'Provide a different username'.format(new_user_obj.username),
                  category='primary')
            return redirect(url_for('user.signup'))

        # add user object to session and commit to db
        db.session.add(new_user_obj)
        db.session.commit()
        flash('Addition of new user {} successful'.format(request.form['username']),
              category='success')
        return redirect(url_for('user.dashboard', username=current_user.username))
    return render_template('/signup.html', form=form)


@user_bp.route('/login', methods=['GET', 'POST'])
def login_home():
    """login page"""
    # deal with a currently logged user pressing login
    if current_user.is_authenticated:
        flash('User {} already logged in'.format(current_user.username),
              category='primary')
        return redirect(url_for('user.dashboard',
                                username=current_user.username))

    form = LoginForm()
    if form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']
        check_user, user_obj = _check_user_password(username=username,
                                                    password=password)
        if check_user:
            login_user(user=user_obj)
            next_page = request.form['next']
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('user.dashboard', username=username)
            flash('You are successfully logged in', category='success')
            return redirect(next_page)
        else:
            flash('Wrong username or password', category='error')
            return render_template('/login.html', form=form)
    else:
        return render_template('/login.html', form=form)


def _check_user_password(username, password):
    """check if password hash in db matches given username and password"""
    user_obj = db.session.query(User).filter(User.username == username).first()
    if user_obj is not None:
        if flask_bcrypt.check_password_hash(user_obj.password_hash, password.encode('utf-8')):
            return True, user_obj
        else:
            return False, None
    else:
        return False, None


def _compare_password(username, new_password):
    """compare old and new password hashes"""
    user_obj = db.session.query(User).filter(User.username == username).first()
    if user_obj is not None:
        if flask_bcrypt.check_password_hash(user_obj.password_hash, new_password.encode('utf-8')):
            return True
        else:
            return False
    return False


@user_bp.route('/logout')
def logout_home():
    """logout user"""
    if current_user.is_username_exist():
        username = current_user.username
    logout_user()
    flash('User {} logged out succesfully'.format(username),
          category='success')
    return redirect(url_for('admin.index'))


@user_bp.route('/dashboard')
def dashboard_no_login():
    """dashboard without username input - redirect to login page"""
    flash('Need to login to access user dashboard',
          category='error')
    return redirect(url_for('user.login_home'))


@user_bp.route('/dashboard/<username>')
@login_required     # removed until debugging is complete
def dashboard(username):
    """route to user dashboard"""
    user_obj = User.query.filter(User.username == username).first()
    if user_obj is None:
        flash('No user with username {} exist'.format(username),
              category='error')
        return redirect(url_for('user.login_home'))
    return render_template('/dashboard.html', user=user_obj)


@user_bp.route('/search', methods=['GET', 'POST'])
# @login_required
def search():
    """search user in db - follows same template as search customer"""
    form = SearchUserCategory()
    if form.validate_on_submit():
        return redirect(url_for('user.search_user', category=request.form['search_by']))

    return render_template('/search_user.html', form=form)


@user_bp.route('/search/<category>', methods=['GET', 'POST'])
def search_user(category):
    """search user based on category given"""

    form = SearchUser()
    remove_form = RemoveUser()
    data = []

    if category == 'userid':
        del form.first_name, form.last_name, form.username, form.phone_num, form.email
    elif category == 'firstname':
        del form.user_id, form.last_name, form.username, form.phone_num, form.email
    elif category == 'lastname':
        del form.user_id, form.first_name, form.username, form.phone_num, form.email
    elif category == 'username':
        del form.user_id, form.first_name, form.last_name, form.phone_num, form.email
    elif category == 'phone':
        del form.user_id, form.first_name, form.last_name, form.username, form.email
    elif category == 'email':
        del form.user_id, form.first_name, form.last_name, form.username, form.phone_num
    elif category == 'all':
        del form.user_id, form.first_name, form.last_name, form.username, \
            form.phone_num, form.email

    if form.validate_on_submit():
        # search customer in db
        if category == 'userid':
            data = request.form['user_id']
        elif category == 'firstname':
            data = request.form['first_name']
        elif category == 'lastname':
            data = request.form['last_name']
        elif category == 'username':
            data = request.form['username']
        elif category == 'phone':
            data = request.form['phone_num-country_code'] + \
                   request.form['phone_num-phone_num']
        elif category == 'email':
            data = request.form['email']
        elif category == 'all':
            data = request.form
        else:
            data = []

        users = _search_user_in_db(data, category)
        if not users:
            flash(message='no users found with given details', category='error')

        return render_template('/search_result.html', form=form,
                               category=category, result=users, remove_form=remove_form)

    return render_template('/search.html', category=category, form=form)


@user_bp.route('/remove', methods=['GET', 'POST'])
# @login_required
def remove():
    """remove user from db"""
    form = RemoveUser()
    review_form = SignupForm()
    review_list = []
    username = ''
    if form.validate_on_submit():
        # retrieve customer with matching customer id
        username = request.form['username']
        review_list = db.session.query(User). \
            filter(User.username == username).first()

        if review_list is not None:
            # customer table
            review_form.first_name.data = review_list.firstname
            review_form.last_name.data = review_list.lastname
            # review_form.phone_num.phone_num.data = review_list.phone
            review_form.email.data = review_list.email
            review_form.username.data = review_list.username

            return render_template('/remove.html', form=form, result=review_list,
                                   review_form=review_form, username=username)
        else:
            flash('User with username {} does not exist'.format(username), category='error')
            return redirect(url_for('user.search'))

    return render_template('/remove.html', form=form, result=review_list,
                           review_form=review_form, username=username)


@user_bp.route('/remove/<username>', methods=['GET'])
def remove_user(username):
    """remove specific customer with customer_id from db"""
    # run delete row query on customer/address/taxinfo
    db.session.query(User).filter(User.username == username).delete()
    db.session.commit()

    flash(message='User with username {} removed'.format(username), category='success')
    return redirect(url_for('user.remove'))


@user_bp.route('/<username>/change_password', methods=['GET', 'POST'])
# @login_required
def change_password(username):
    """change password for logged in user"""
    form = ChangePassword()
    if form.validate_on_submit():
        old_password = request.form['old_pass']
        # new_password = request.form['password']
        # check if current password is correct
        check_user, user_obj = _check_user_password(username=username,
                                                    password=old_password)
        if check_user:
            if not _compare_password(username, new_password=request.form['password']):
                user_obj.set_password(request.form['password'])
                # new_user_obj.set_added_user(current_user.username)

                # add user object to session and commit to db
                db.session.add(user_obj)
                db.session.commit()
                flash('Password changed successfully',
                      category='success')
                return redirect(url_for('user.dashboard', username=username))

            flash('New password cannot be the same as old password.',
                  category='error')
            return render_template('change_password.html', form=form)

        else:
            flash('Wrong password. Enter correct current password to proceed',
                  category='error')
            return redirect(url_for('user.change_password', username=username))

    return render_template('change_password.html', form=form)


def _search_user_in_db(value, category):
    """seacrh for customer given in form object in db"""

    # customers = None
    if category == 'customerid':
        users = db.session.query(User).filter(User.id == value).all()
    elif category == 'firstname':
        users = db.session.query(User).filter(User.firstname == value).all()
    elif category == 'lastname':
        users = db.session.query(User).filter(User.lastname == value).all()
    elif category == 'fullname':
        users = db.session.query(User).filter(User.fullname == value).all()
    elif category == 'username':
        users = db.session.query(User).filter(User.username == value).all()
    elif category == 'email':
        users = db.session.query(User).filter(User.email == value).all()
    elif category == 'phone':
        users = db.session.query(User).filter(User.phone == value).all()
    elif category == 'all':
        users = db.session.query(User).all()
    else:
        users = []
    return users


@user_bp.route('/overview')
# @login_required
def user_overview():
    """overview page for users"""
    return render_template('user_overview.html')
