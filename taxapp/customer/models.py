from flask_login import UserMixin
from taxapp import db, flask_bcrypt
from taxapp import login_manager


class Customer(UserMixin, db.Model):
    __tablename__ = 'test_customers'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    fullname = db.Column(db.String(40), index=True)
    email = db.Column(db.String(30), index=True)
    phone = db.Column(db.String(10))
    type = db.Column(db.Enum('personal', 'commercial', name='customer_type'), nullable=False)
    date_added = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    added_user = db.Column(db.String(20))
    updated_user = db.Column(db.String(20))

    def set_full_name(self):
        """set value of fullname column using first and last name"""
        self.fullname = self.firstname + ' ' + self.lastname

    def set_full_phone(self, country_code, phone_number):
        """set phone number with country code"""
        self.phone = country_code + phone_number

    def set_added_user(self, change_type, username):
        """set added_user and updated_user"""
        if change_type == 'add':
            self.added_user = username
        elif change_type == 'update':
            self.updated_user = username

    def __repr__(self):
        return f"Customer(id={self.id!r}, name={self.fullname!r}, email={self.email!r}, " \
               f"phone={self.phone!r}, type={self.type!r}, added_on={self.date_added!r})"
