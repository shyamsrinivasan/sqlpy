from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(30))
    lastname = Column(String(30))
    email = Column(String(30))
    phone = Column(Integer)

    def __repr__(self):
        return f"User(id={self.id!r}, firstname={self.firstname!r}, lastname={self.lastname!r})"


class Identity(Base):
    __tablename__ = 'identity'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('customer.id'))
    pan = Column(String(12), index=True)

    def __repr__(self):
        return f"Identity(id={self.id!r}, user_id={self.user_id!r}, pan={self.pan!r})"
    