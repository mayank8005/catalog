import sys
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# declaration of user items table
class Items(Base):
    # setting name of the table
    __tablename__ = 'items'

    # declaration of table attributes
    # using item name as primary key
    item_name = Column(String(256), primary_key=True)  # store name of item
    category = Column(String(100), nullable=False)  # predefined category
    item_description = Column(String(500))     # stores description of item
    user_id = Column(Integer, ForeignKey('users.id'))  # stores uploader's id
    users = relationship(Users)


class Users(Base):

    # setting name of the table
    __tablename__ = 'users'

    # declaration of table attributes
    id = Column(Integer, primary_key=True)  # used as primary key
    name = Column(String(100), nullable=False)   # name of the user
    email = Column(String(256))     # email of user
    picture = Column(String(256))   # URL of user's profile picture

# creating engine for sqlalchemy
engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)