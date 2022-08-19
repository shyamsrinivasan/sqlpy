from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# mixin class to serve as base class for mapping to reflected tables
class Reflected(DeferredReflection):
    __abstract__ = True


class Customer(Reflected, Base):
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(30))
    lastname = Column(String(30))
    email = Column(String(30))
    phone = Column(Integer)

    taxes = relationship("TaxInfo", back_populates="customer_info", cascade="all, delete")
    charges = relationship("Transactions", back_populates="customer_info")


class TaxInfo(Reflected, Base):
    """class with all tax-related information on client"""
    __tablename__ = 'tax_info'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('customer.id'))
    pan = Column(String(12), index=True, nullable=False)
    # add columns: portal_password, aadhaar

    customer_info = relationship("Customer", back_populates="taxes")


def reflect_table(engine):
    """reflect table from DB given an create_engine instance"""
    Reflected.prepare(engine)
