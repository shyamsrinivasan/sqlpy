from flask import Blueprint


bills_bp = Blueprint('bills', __name__, template_folder='templates')
from . import views, forms, models
