from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy import ForeignKey, Enum

Base = declarative_base()


class Reflected(DeferredReflection):
    """mixin class to serve as base class for
    mapping to reflected tables"""
    __abstract__ = True


class User(Reflected, Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(15))
    lastname = Column(String(15))
    fullname = Column(String(30), index=True)
    email = Column(String(30))


class Customer(Reflected, Base):
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True)
    fullname = Column(String(30), index=True, nullable=False)
    email = Column(String(30))
    phone = Column(String(10))
    firstname = Column(String(15), index=True)
    lastname = Column(String(15), index=True)
    # customer_type = Column(String(15))
    type = Column(Enum('personal', 'commercial', name='customer_type'), nullable=False)
    date_added = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    date_updated = Column(DateTime(timezone=True), onupdate=func.now())

    taxes = relationship("TaxInfo", back_populates="customer_info",
                         cascade="all, delete", uselist=False)
    # taxes = relationship("TaxInfo")
    address_info = relationship('Address', back_populates='customer_info',
                                cascade="all, delete", uselist=False)
    charges = relationship("Transactions", back_populates="customer_info")

    def get_column(self, column_name=None):
        """retrieve column object for table"""
        return self.__table__.columns[column_name]

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.fullname!r}, email={self.email!r}, " \
               f"phone={self.phone!r}, type={self.customer_type!r}, added_on={self.date_added!r})"


class TaxInfo(Reflected, Base):
    """class with all tax-related information on client"""
    __tablename__ = 'tax_info'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id', onupdate='CASCADE',
                                             ondelete='CASCADE'), nullable=False)
    customer_name = Column(String(30), index=True, nullable=False)
    pan = Column(String(12), index=True, nullable=False, unique=True)
    aadhaar = Column(String(12), index=True, nullable=False, unique=False)
    date_added = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    # add columns: portal_password

    customer_info = relationship("Customer", back_populates="taxes",
                                 cascade="all, delete")

    def get_column(self, column_name=None):
        """retrieve column object for table"""
        return self.__table__.columns[column_name]

    def __repr__(self):
        return f"TaxInfo(id={self.id!r}, customer_id={self.customer_id!r}, " \
               f"name={self.customer_name!r}, pan={self.pan!r}, " \
               f"aadhaar={self.aadhaar!r}, added_on={self.date_added!r})"


class Address(Reflected, Base):
    """class for address table with address for all customers"""

    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id', onupdate='CASCADE',
                                             ondelete='CASCADE'), nullable=False)
    customer_name = Column(String(30), index=True)
    # add address columns from taxdata db table
    # type = Column(Enum('house', 'apartment', 'business - single',
    #                    'business - complex', name='address_type'))
    street_num = Column(String(8))
    street_name = Column(String(30))
    house_num = Column(String(8))
    locality = Column(String(30))
    city = Column(String(20), nullable=False)
    state = Column(String(15), nullable=False, server_default='Tamil Nadu')
    pin = Column(String(6), nullable=False)
    date_added = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_update = Column(DateTime(timezone=True), onupdate=func.now())

    customer_info = relationship('Customer', back_populates='address_info',
                                 cascade='all, delete')

    def __repr__(self):
        return f"Address(id={self.id!r}, customer_id={self.customer_id!r}, " \
               f"name={self.customer_name!r}, locality={self.locality!r}, " \
               f"city={self.city!r}, pin={self.pin!r}, " \
               f"added_on={self.date_added!r})"


class Transactions(Reflected, Base):
    """class with list of all transactions done for all customers"""

    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    customer_id = Column(Integer, ForeignKey('customer.id', onupdate='CASCADE',
                                             ondelete='CASCADE'), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    amount = Column(Float)
    # status = Column(String(15), index=True, nullable=False, server_default='complete')
    status = Column(Enum('pending', 'complete', 'failed', name='payment_status'),
                    nullable=False, server_default='pending')
    paid_on = Column(DateTime(timezone=True), onupdate=func.now())
    # add columns: performed_by

    customer_info = relationship("Customer", back_populates="charges")

    def __repr__(self):
        return f"Transactions(id={self.id!r}, date = {self.date!r}, " \
               f"customer_id={self.customer_id!r}, " \
               f"transaction_type = {self.transaction_type!r}, amount={self.amount!r}," \
               f"status={self.status!r})"


def create_table(engine):
    """create tables from declarative classes in DB defined in engine"""
    Base.metadata.create_all(engine)


def drop_table(engine):
    """drop all tables in DB through engine"""
    Base.metadata.drop_all(engine)
