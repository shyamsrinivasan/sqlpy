from flask_login import UserMixin
from taxapp import db, flask_bcrypt
from taxapp import login_manager


class Customer(db.Model):
    __tablename__ = 'test_customers'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    fullname = db.Column(db.String(40), index=True)
    email = db.Column(db.String(30), index=True)
    phone = db.Column(db.String(14))
    type = db.Column(db.Enum('personal', 'commercial', name='customer_type'), nullable=False)
    date_added = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    added_user = db.Column(db.String(20))
    updated_user = db.Column(db.String(20))

    address_info = db.relationship('Address', back_populates='customer_info',
                                   cascade="all, delete", uselist=False)

    def set_full_name(self):
        """set value of fullname column using first and last name"""
        self.fullname = self.firstname + ' ' + self.lastname
        return self.fullname

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


class Address(db.Model):
    __tablename__ = 'test_address'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('test_customers.id', onupdate='CASCADE',
                                                      ondelete='CASCADE'), nullable=False)
    customer_name = db.Column(db.String(30), index=True)

    # add address columns from taxdata db table
    type = db.Column(db.Enum('house', 'apartment', 'business - single',
                             'business - complex', name='address_type'))
    street_num = db.Column(db.String(8))
    street_name = db.Column(db.String(30))
    house_num = db.Column(db.String(8))
    locality = db.Column(db.String(30))
    city = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(15), nullable=False, server_default='Tamil Nadu')
    pin = db.Column(db.String(6), nullable=False)
    added_user = db.Column(db.String(20))
    date_added = db.Column(db.DateTime(timezone=True), nullable=False,
                           server_default=db.func.now())
    updated_user = db.Column(db.String(20))
    last_update = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    customer_info = db.relationship('Customer', foreign_keys='Customer.id',
                                    back_populates='address_info',
                                    cascade='all, delete')

    def set_added_user(self, change_type, username):
        """set added_user and updated_user"""
        if change_type == 'add':
            self.added_user = username
        elif change_type == 'update':
            self.updated_user = username

    def __repr__(self):
        return f"Address(id={self.id!r}, customer_id={self.customer_id!r}, " \
               f"name={self.customer_name!r}, locality={self.locality!r}, " \
               f"city={self.city!r}, pin={self.pin!r}, " \
               f"added_on={self.date_added!r})"
