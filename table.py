from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy import ForeignKey

Base = declarative_base()


class Reflected(DeferredReflection):
    """mixin class to serve as base class for
    mapping to reflected tables"""
    __abstract__ = True

    # def reflect_tabe(self, engine):
    #     self.prepare(engine)


class Customer(Reflected, Base):
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(15))
    lastname = Column(String(15))
    email = Column(String(30))
    phone = Column(String(10))
    fullname = Column(String(30), index=True)
    customer_type = Column(String(15))

    taxes = relationship("TaxInfo", back_populates="customer_info",
                         cascade="all, delete", uselist=False)
    # taxes = relationship("TaxInfo")
    charges = relationship("Transactions", back_populates="customer_info")

    def get_column(self, column_name=None):
        """retrieve column object for table"""
        return self.__table__.columns[column_name]

    def __repr__(self):
        return f"User(id={self.id!r}, firstname={self.firstname!r}, lastname={self.lastname!r})"


class TaxInfo(Reflected, Base):
    """class with all tax-related information on client"""
    __tablename__ = 'tax_info'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('customer.id', onupdate='CASCADE', ondelete='CASCADE'))
    user_name = Column(String(30), index=True)
    pan = Column(String(12), index=True, nullable=False)
    aadhaar = Column(String(12), index=True, nullable=False)
    # add columns: portal_password

    customer_info = relationship("Customer", back_populates="taxes", cascade="all, delete")

    def get_column(self, column_name=None):
        """retrieve column object for table"""
        return self.__table__.columns[column_name]

    def __repr__(self):
        return f"Identity(id={self.id!r}, user_id={self.user_id!r}, pan={self.pan!r})"


class Transactions(Reflected, Base):
    """class with list of all transactions done for all customers"""

    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    date = Column(TIMESTAMP)
    user_id = Column(Integer, ForeignKey('customer.id'))
    transaction_type = Column(String(50), nullable=False)
    cost = Column(Float)
    # add columns: performed_by

    customer_info = relationship("Customer", back_populates="charges")

    def __repr__(self):
        return f"Identity(id={self.id!r}, date = {self.date!r}, user_id={self.user_id!r}, " \
               f"transaction_type = {self.transaction_type!r}, cost={self.cost!r})"


def create_table(engine):
    """create tables from declarative classes in DB defined in engine"""
    Base.metadata.create_all(engine)


def drop_table(engine):
    """drop all tables in DB through engine"""
    Base.metadata.drop_all(engine)
