from flask import Blueprint


customer_bp = Blueprint('customer', __name__, template_folder='templates')
from . import views, forms, models