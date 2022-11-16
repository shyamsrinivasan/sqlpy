from flask import render_template, redirect, url_for
from . import admin_bp
from .forms import ContactForm
from flask_login import login_required


@admin_bp.route('/')
@admin_bp.route('/index')
def index():
    """home page"""
    return render_template('/index.html')


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
