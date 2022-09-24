from taxapp import db, flask_bcrypt
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from . import admin_bp
from .forms import LoginForm
from .models import User


@admin_bp.route('/')
@admin_bp.route('/index')
def index():
    """home page"""
    return render_template('/index.html')


@admin_bp.route('/login', methods=['GET', 'POST'])
def login_home():
    """login page"""
    # deal with a currently signed in user pressing login
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']
        check_user, user_obj = _check_user_password(username=username,
                                                    password=password)
        if check_user:
            login_user(user=user_obj)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('admin.index')
            return redirect(next_page)
        else:
            return 'Wrong username or password', 404
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
    logout_user()
    return redirect(url_for('admin.index'))


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
    # form = ContactForm()
    # if form.validate_on_submit():
    #     return redirect(url_for('home.success', from_page='contact'))
    return render_template('/contact.html')


