from taxapp import db


class Customer(db.Model):
    __tablename__ = 'test_customers'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    fullname = db.Column(db.String(40), index=True)
    type = db.Column(db.Enum('personal', 'commercial', name='customer_type'), nullable=False)
    date_added = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    added_user = db.Column(db.String(20))
    updated_user = db.Column(db.String(20))

    address_info = db.relationship('Address', back_populates='customer_info',
                                   cascade="all, delete", uselist=False)
    identity_info = db.relationship('Identity', back_populates='identity_customer_info',
                                    cascade="all, delete", uselist=False)
    contact_info = db.relationship('Contact', back_populates='contact_customer_info',
                                   cascade="all, delete", uselist=False)

    def set_full_name(self):
        """set value of fullname column using first and last name"""
        self.fullname = self.firstname + ' ' + self.lastname
        return self.fullname

    def set_added_user(self, change_type, username):
        """set added_user and updated_user"""
        if change_type == 'add':
            self.added_user = username
        elif change_type == 'update':
            self.updated_user = username

    def is_customer_exist(self):
        """check if user object row already exists in db with given username"""
        customer_obj = db.session.query(Customer).filter(Customer.fullname == self.fullname).first()
        if customer_obj is not None:
            return True
        else:
            return False

    def __repr__(self):
        return f"Customer(id={self.id!r}, name={self.fullname!r}, " \
               f"type={self.type!r}, added_on={self.date_added!r})"


class Address(db.Model):
    __tablename__ = 'test_address'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('test_customers.id', onupdate='CASCADE',
                                                      ondelete='CASCADE'), nullable=False)
    customer_name = db.Column(db.String(40), index=True)

    # add address columns from taxdata db table
    type = db.Column(db.Enum('house', 'apartment', 'store-single',
                             'store-complex', name='address_type'), default='house')
    street_num = db.Column(db.String(8))
    street_name = db.Column(db.String(30))
    house_num = db.Column(db.String(8))
    locality = db.Column(db.String(30))
    locality_2 = db.Column(db.String(30))
    city = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(15), nullable=False, server_default='Tamil Nadu')
    pin = db.Column(db.String(6), nullable=False)
    added_user = db.Column(db.String(20))
    date_added = db.Column(db.DateTime(timezone=True), nullable=False,
                           server_default=db.func.now())
    updated_user = db.Column(db.String(20))
    last_update = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    customer_info = db.relationship('Customer', back_populates='address_info',
                                    cascade='all, delete')

    def set_added_user(self, change_type, username):
        """set added_user and updated_user"""
        if change_type == 'add':
            self.added_user = username
        elif change_type == 'update':
            self.updated_user = username

    def set_customer_id(self, customer_id):
        """set customer id of identity object"""
        # if change_type == 'add':
        self.customer_id = customer_id

    def is_customer_exist(self):
        """check if user object row already exists in db with given username"""
        address_obj = db.session.query(Address).filter(Address.customer_id ==
                                                       self.customer_id).first()
        if address_obj is not None:
            return True
        else:
            return False

    def __repr__(self):
        return f"Address(id={self.id!r}, customer_id={self.customer_id!r}, " \
               f"name={self.customer_name!r}, locality={self.locality!r}, " \
               f"city={self.city!r}, pin={self.pin!r}, " \
               f"added_on={self.date_added!r})"


class TaxInfo(db.Model):
    __tablename__ = 'test_taxinfo'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('test_customers.id', onupdate='CASCADE',
                                                      ondelete='CASCADE'), nullable=False)
    customer_name = db.Column(db.String(30), index=True)


class Identity(db.Model):
    __tablename__ = 'test_identity'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('test_customers.id', onupdate='CASCADE',
                                                      ondelete='CASCADE'), nullable=False)
    customer_name = db.Column(db.String(40), nullable=False)

    dob = db.Column(db.Date, nullable=False)
    pan = db.Column(db.String(10), nullable=False, index=True)
    aadhaar = db.Column(db.String(12))
    added_user = db.Column(db.String(20))
    date_added = db.Column(db.DateTime(timezone=True), nullable=False,
                           server_default=db.func.now())
    updated_user = db.Column(db.String(20))
    last_update = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    identity_customer_info = db.relationship('Customer', back_populates='identity_info',
                                             cascade='all, delete')

    def set_customer_id(self, customer_id):
        """set customer id of identity object"""
        # if change_type == 'add':
        self.customer_id = customer_id
        # elif change_type == 'update':
        #     self.customer_id = customer_id

    def is_customer_name_exist(self):
        """check if identity object row already exists in db with given name"""
        id_name_obj = db.session.query(Identity).filter(Identity.customer_name ==
                                                        self.customer_name).first()
        if id_name_obj is not None:
            return True

        return False

    def is_customer_pan_exist(self):
        """check if identity object row exists in db with given pan"""
        identity_obj = db.session.query(Identity).filter(Identity.pan == self.pan).first()
        if identity_obj is not None:
            return True

        return False

    def is_customer_exist(self):
        identity_info = db.session.query(Identity).\
            filter(Identity.customer_name == self.customer_name,
                   Identity.pan == self.pan).first()
        if identity_info:
            return True
        return False

    def set_added_user(self, change_type, username):
        """set added_user and updated_user"""
        if change_type == 'add':
            self.added_user = username
        elif change_type == 'update':
            self.updated_user = username

    def __repr__(self):
        return f"Identity(id={self.id!r}, customer_id={self.customer_id!r}, " \
               f"name={self.customer_name!r}, dob={self.dob!r}, " \
               f"pan={self.pan!r}, aadhaar={self.aadhaar!r})"


class Contact(db.Model):
    __tablename__ = 'test_contact'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('test_customers.id', onupdate='CASCADE',
                                                      ondelete='CASCADE'), nullable=False)
    customer_name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(30), index=True)
    country_code = db.Column(db.String(4))
    phone = db.Column(db.String(10))

    date_added = db.Column(db.DateTime(timezone=True), nullable=False,
                           server_default=db.func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    added_user = db.Column(db.String(20))
    updated_user = db.Column(db.String(20))

    contact_customer_info = db.relationship('Customer', back_populates='contact_info',
                                            cascade='all, delete')

    def set_added_user(self, change_type, username):
        """set added_user and updated_user"""
        if change_type == 'add':
            self.added_user = username
        elif change_type == 'update':
            self.updated_user = username

    def set_customer_id(self, customer_id):
        """set customer id of identity object"""
        self.customer_id = customer_id

    def __repr__(self):
        return f"Contact(id={self.id!r}, name={self.customer_name!r}, email={self.email!r}, " \
               f"phone={self.country_code + self.phone!r}, added_on={self.date_added!r})"
