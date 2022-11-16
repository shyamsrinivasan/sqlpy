from flask import render_template
from . import admin_bp
from taxapp import db


@admin_bp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@admin_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
