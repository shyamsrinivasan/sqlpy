from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy import Float
from sqlalchemy.orm import declarative_base, relationship, Session

Base = declarative_base()


class Customer(Base):
    """class with customer details only"""
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(30))
    lastname = Column(String(30))
    email = Column(String(30))
    phone = Column(Integer)

    taxes = relationship("TaxInfo", back_populates="customer_info", cascade="all, delete")
    charges = relationship("Transactions", back_populates="customer_info")

    def __repr__(self):
        return f"User(id={self.id!r}, firstname={self.firstname!r}, lastname={self.lastname!r})"


class TaxInfo(Base):
    """class with all tax-related information on client"""
    __tablename__ = 'tax_info'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('customer.id'))
    pan = Column(String(12), index=True, nullable=False)
    # add columns: portal_password, aadhaar

    customer_info = relationship("Customer", back_populates="taxes")

    def __repr__(self):
        return f"Identity(id={self.id!r}, user_id={self.user_id!r}, pan={self.pan!r})"


class Transactions(Base):
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


def add_row(engine):
    """add data to table in db"""
    with Session(engine) as session:

