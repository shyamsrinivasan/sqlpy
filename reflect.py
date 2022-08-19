from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import declarative_mixin, declared_attr

Base = declarative_base()


# mixin class to serve as base class for mapping to reflected tables
class Reflected(DeferredReflection):
    __abstract__ = True


# @declarative_mixin
# class MyMixin:
#     @declared_attr
#     def __tablename__(cls):
#         return cls.__name__.lower()
#
#     __table_args__ = {"mysql_engine": "InnoDB"}
#     __mapper_args__ = {"always_refresh": True}
#
#     id = Column(Integer, primary_key=True)


# @declarative_mixin
# class TimeStampMixin:
#     created_on = Column(DateTime, default=func.now())


class Customer(Reflected, Base):
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(30))
    lastname = Column(String(30))
    email = Column(String(30))
    phone = Column(Integer)

    taxes = relationship("TaxInfo", back_populates="customer_info", cascade="all, delete")
    # charges = relationship("Transactions", back_populates="customer_info")


# @declarative_mixin
# class UserIdMixin:
#     @declared_attr
#     def user_id(cls):
#         return Column(Integer, ForeignKey('customer.id'))
#
#     @declared_attr
#     def user(cls):
#         return relationship("Customer", back_populates="taxes")


class TaxInfo(Reflected, Base):
    """class with all tax-related information on client"""
    __tablename__ = 'tax_info'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('customer.id'))
    pan = Column(String(12), index=True, nullable=False)
    # add columns: portal_password, aadhaar

    customer_info = relationship("Customer", back_populates="taxes")


def reflect_table(engine):
    """reflect table from DB given a create_engine instance"""
    Reflected.prepare(engine)
