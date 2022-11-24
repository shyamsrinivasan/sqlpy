from taxapp import db


class Items(db.Model):
    __tablename__ = 'test_items'

    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('test_bills.id',
                                                  ondelete='CASCADE'))
    bill_item = db.Column(db.String(40), nullable=False)
    item_cost = db.Column(db.Float)

    def __repr__(self):
        return f"Billing(id={self.id!r}, bill number={self.bill_id!r}, item={self.bill_item!r}, " \
               f"cost={self.item_cost!r})"


class Bill(db.Model):
    __tablename__ = 'test_bills'

    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(11), nullable=False, index=True)
    customer_name = db.Column(db.String(30), db.ForeignKey('test_customers.fullname',
                                                           onupdate='CASCADE',
                                                           ondelete='CASCADE'),
                              nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('test_customers.id', onupdate='CASCADE',
                                                      ondelete='CASCADE'), nullable=False)
    pan = db.Column(db.String(10), nullable=False, index=True)
    # bill_date = db.Column(db.DateTime(timezone=True), default=db.func.now())
    # user_name = db.Column(db.String(40), db.ForeignKey('test_users.fullname', onupdate='CASCADE',
    #                                                    ondelete='CASCADE'), nullable=False)
    # user_name = db.Column(db.String(40), nullable=False)
    items = db.relationship('Items')
    # bill_item = db.Column(db.String(40), nullable=False)
    # price = db.Column(db.Float)
    # quantity = db.Column(db.Integer)
    # item_cost = db.Column(db.Float)

    customer_id_info = db.relationship('Customer', foreign_keys="[Bill.customer_id]",
                                       back_populates='bill_info',
                                       cascade='all, delete')
    customer_name_info = db.relationship('Customer', foreign_keys="[Bill.customer_name]")

    def __repr__(self):
        return f"Billing(id={self.id!r}, name={self.customer_name!r}, " \
               f"bill_no={self.bill_number!r}, pan={self.pan!r})"
