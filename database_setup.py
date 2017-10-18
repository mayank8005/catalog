import sys
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Users(Base):

    # setting name of the table
    __tablename__ = 'users'

    # declaration of table attributes
    id = Column(Integer, primary_key=True)  # used as primary key
    name = Column(String(100), nullable=False)   # name of the user
    email = Column(String(256), nullable=False)     # email of user
    picture = Column(String(256))   # URL of user's profile picture


# declaration of user items table
class Items(Base):
    # setting name of the table
    __tablename__ = 'items'

    # declaration of table attributes
    # using item name as primary key
    id = Column(Integer, autoincrement=True, nullable=False, unique=True)
    name = Column(String(256), primary_key=True)  # store name of item
    category = Column(String(100), nullable=False)  # predefined category
    description = Column(String(500))     # stores description of item
    user_id = Column(Integer, ForeignKey('users.id'))  # stores uploader's id
    users = relationship(Users)


# creating engine for sqlalchemy
engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)