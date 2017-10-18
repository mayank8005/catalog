import bleach
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from database_setup import Users, Base, Items


class ItemsDatabase:
    """ This class will handle/perform database related operations or CURD
        operation to our item database.Other classes can use its object to
        communicate with database"""

    def __init__(self):
        engine = create_engine('sqlite:///catalog.db')
        Base.metadata.bind = engine

        db_session = sessionmaker(bind=engine)
        self.session = db_session()

    def get_latest(self):
        """This method returns list of 10 most recently inserted items"""
        try:
            latest_items = self.session.query(Items).order_by(
             Items.id.desc()).limit(10).all()
        except NoResultFound:
            latest_items = None
        return latest_items

    def get_items(self, category):
        """This method returns list of all items belonging to
        particular category
        :parameter category: specify category from which items are extracted"""

        try:
            items = self.session.query(Items).filter_by(category=category).all()
        except NoResultFound:
            items = None
        return items

    def get_item(self, name):
        """This method return an item object
        :parameter name: specify name of the item to be extracted"""

        item = self.session.query(Items).filter_by(name=name).one_or_none()
        return item

    def edit_item(self, item, name=None, description=None, category=None):
        """This method updates an existing item
        :parameter item: item to be updated
        :parameter name: updated name (Optional)(Type String)
        :parameter description: updated description(Optional)(Type String)
        :parameter category: updated category(Optional)(Type String)
        """
        if name is None:
            name = item.name
        # checking condition in bleach format as we have stored name in bleached
        #  form.
        # checking this condition as user may not want to change item name in
        # that case bleached.clean(name) == item.name
        elif bleach.clean(name) != item.name:
            # checking for same duplication
            # As name should be unique in our list we have to check other items
            # if they are having same name or not
            if self.get_item(bleach.clean(name)) is not None:
                return False
        if description is None:
            description = item.description
        if category is None:
            category = item.category

        # using bleach we are protecting our db from XSS attacks
        item.name = bleach.clean(name)
        item.description = bleach.clean(description)
        item.category = bleach.clean(category)

        self.session.add(item)
        self.session.commit()
        return True

    def add_item(self, name, description, category, user_id):
        """
        This method add item in our database
        :parameter name: name of item to be created
        :parameter description: description of item to be created
        :parameter category: category of item to be created
        :parameter user_id: id of user/owner
        """

        # cleaning parameter via bleach for protection against xss
        item_name = bleach.clean(name)
        item_description = bleach.clean(description)
        item_category = bleach.clean(category)

        # checking for same name
        # we are checking bleached version because we have stored name in
        # bleached form in our database
        # if item in same name exist then function will return false
        if name == self.get_item(bleach.clean(name)):
            return False

        # creating item object
        item = Items(name=item_name, description=item_description,
                     category=item_category, user_id=user_id)

        self.session.add(item)
        self.session.commit()
        return True

    def delete_item(self, name):
        """this method deletes existing item from our database
        :parameter name: name of the item to be deleted
        """
        try:
            item = self.session.query(Items).filter_by(name=name).one()
            self.session.delete(item)
            self.session.commit()
            return True
        except NoResultFound:
            return False

    def check_id(self, email):
        """checks that user with particular id exist or not
        :parameter email: email of user
        """
        user = self.session.query(Users).filter_by(email=email).one_or_none()
        if user is None:
            return False        # user does not exist
        else:
            return True         # user exist

    def add_user(self, name, email, picture):
        """add user in our database
        :parameter email: email of user
        :parameter name: name of user
        :parameter picture: url of profile picture of user
        """
        user = Users(name=name, email=email, picture=picture)
        self.session.add(user)
        self.session.commit()

    def get_user(self, email):
        """returns user item having particular email
        parameter email: email of user
        """

        user = self.session.query(Users).filter_by(email=email).one_or_none()

        return user
