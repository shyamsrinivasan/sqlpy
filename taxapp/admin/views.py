from flask import render_template, request, redirect, url_for, flash
from . import admin_bp
from .forms import LoginForm, ContactForm, SignupForm
from .models import User
from taxapp import db, flask_bcrypt
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@admin_bp.route('/')
@admin_bp.route('/index')
def index():
    """home page"""
    return render_template('/index.html')


@admin_bp.route('/signup', methods=['GET', 'POST'])
@login_required
def signup():
    """take user details in form to create User object and
        add as row to user table"""
    form = SignupForm()
    if form.validate_on_submit():
        # process sign-up information using func into db add info to db here
        # generate user object
        new_user_obj = User(firstname=request.form['first_name'],
                            lastname=request.form['last_name'],
                            email=request.form['email'],
                            phone=request.form['phone'],
                            username=request.form['username'])
        # add hashed password to db
        new_user_obj.set_password(request.form['password'])

        # check if user with username exists and redirect to enter data again
        if new_user_obj.is_username_exist():
            return redirect(url_for('admin.signup'))

        # check if user with firstname/lastname exists and redirect to enter data again
        if new_user_obj.is_user_exist():
            return redirect(url_for('admin.signup'))

        # add user object to session and commit to db
        db.session.add(new_user_obj)
        db.session.commit()
        flash('Addition of new user {} successful'.format(form.username))
        return redirect(url_for('admin.success', from_page='signup'))
    return render_template('/signup.html', form=form)


@admin_bp.route('/login', methods=['GET', 'POST'])
def login_home():
    """login page"""
    # deal with a currently logged user pressing login
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))

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
                next_page = url_for('admin.dashboard', username=username)
            flash('You are successfully logged in', 'info')
            return redirect(next_page)
        else:
            flash('Wrong username or password', 'error')
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


@admin_bp.route('/logout')
def logout_home():
    """logout user"""
    if current_user.is_username_exist():
        username = current_user.username
    logout_user()
    flash('User {} logged out succesfully'.format(username))
    return redirect(url_for('admin.index'))


@admin_bp.route('/dashboard')
def dashboard_no_login():
    """dashboard without username input - redirect to login page"""
    flash('Need to login to access user dashboard', 'error')
    return redirect(url_for('admin.login_home'))


@admin_bp.route('/dashboard/<username>')
@login_required     # removed until debugging is complete
def dashboard(username):
    """route to user dashboard"""
    user_obj = User.query.filter(User.username == username).first()
    if user_obj is None:
        flash('No user with username {} exist'.format(username), 'error')
        return redirect(url_for('admin.login_home'))
    return render_template('/dashboard.html', user=user_obj)


@admin_bp.route('/customers')
@login_required
def customers():
    """route to access various customer related pages"""
    return render_template('/customers.html')


@admin_bp.route('/faq')
def faq():
    """FAQs page"""
    return render_template('/faq.html')


@admin_bp.route('/about')
def about():
    """about page"""
    return render_template('/about.html')


@admin_bp.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    """contact us page"""
    form = ContactForm()
    # if form.validate_on_submit():
    #     return redirect(url_for('home.success', from_page='contact'))
    return render_template('/contact.html', form=form)


@admin_bp.route('/<from_page>/success')
def success(from_page):
    """success page views/routes for different sections of app"""
    # return render_template('/success.html', page=from_page)
    if from_page == 'contact':
        return render_template('/success.html', page=from_page)
    elif from_page == 'signup':
        # return render_template('/signup_success.html')
        # return render_template('/success.html')
        return redirect(url_for('admin.index'))
