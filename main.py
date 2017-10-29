#!/usr/bin/env python3
from flask import Flask, request, make_response, render_template, url_for, \
    redirect, flash, jsonify, abort
from flask import session as login_session
import random
from database import ItemsDatabase
import string
import json
import httplib2
import requests
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# category list storing names of all predefined categories
CATEGORIES = ['Soccer', 'Basketball', 'Baseball', 'Frisbee', 'Snowboarding',
              'Rock Climbing', 'Foosball', 'Skating', 'Hockey']

# storing client id

CLIENT_ID = json.loads(open("/var/www/html/client_secret.json").read())['web'][
    'client_id']

# init Flask instance
app = Flask(__name__)

# making object of ItemsDatabase class
database = ItemsDatabase()


# it init session variable when client is first connected
@app.before_request
def start_session():
    if login_session.get('session', None) is None:
        login_session['session'] = ''.join(
            random.choice(string.ascii_lowercase +
                          string.ascii_uppercase +
                          string.digits) for _ in range(32))

    # checking for CSRF code
    if request.method == "POST":
        token = login_session.pop('_csrf_token', None)

        if not token or (token != request.form.get(
                '_csrf_token') and token != request.args.get('_csrf_token')):
            abort(403)


# home/main page of our catalog application
# can also accessed via '/index'
@app.route('/')
@app.route('/index')
def index():
    login = is_login()
    print(login)
    session_state = login_session['session']
    # getting 10 latest items
    items = database.get_latest()
    if login is True:
        return render_template('index.html', STATE=session_state,
                               categories=CATEGORIES, items=items)
    else:
        return render_template('public_index.html', STATE=session_state,
                               categories=CATEGORIES, items=items)


# display's items belonging to one of the categories
# category (variables in url): specifies category
@app.route('/catalog/<string:category>/items/')
def show_items(category):
    login = is_login()
    session_state = login_session['session']
    # getting all items of that category
    items = database.get_items(category=category)
    if login is True:
        return render_template('items.html', STATE=session_state,
                               categories=CATEGORIES, items=items,
                               current_category=category)
    else:
        return render_template('public_items.html', STATE=session_state,
                               categories=CATEGORIES, items=items,
                               current_category=category)


# display's more info about particular item in the list
# category (variable in url): defines particular category
# item (variable in url): defines particular item
@app.route('/catalog/<string:category>/<string:item>/')
def show_item(category, item):
    login = is_login()
    session_state = login_session['session']
    # getting item from database
    current_item = database.get_item(item)
    # checking authorization
    auth = False
    if current_item.user_id == login_session.get('user_id', ''):
        auth = True

    if login is True:
        return render_template('item.html', STATE=session_state,
                               categories=CATEGORIES, item=current_item,
                               auth=auth)
    else:
        return render_template('public_item.html', STATE=session_state,
                               categories=CATEGORIES, item=current_item)


# adds item in our catalog application
@app.route('/catalog/add/', methods=['GET', 'POST'])
def add_item():
    # handling GET request
    if request.method == 'GET':
        # checking for login
        if is_login() is False:
            # return auth access error
            return make_response('unauthorized access', 401)
        return render_template('add_new.html', categories=CATEGORIES)
    # handling post request
    else:
        # checking for login
        if is_login() is False:
            # return auth access error
            return make_response('unauthorized access', 401)
        # user is logged in
        # extracting form entries
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']

        # trying to create item
        created = database.add_item(name=name,
                                    category=category,
                                    description=description,
                                    user_id=login_session['user_id'])
        # checking item created or not
        if created is True:
            flash('item added')
        else:
            flash('item already exist')
        # redirecting user to item page
        return redirect(url_for('show_item', category=category, item=name))


# This method will edit particular item of our catalog application
# item (variable in url): defines particular item stored in our database
@app.route('/catalog/<string:item>/edit/', methods=['GET', 'POST'])
def edit_item(item):
    # getting item from database
    item = database.get_item(name=item)
    # if item not found
    if item is None:
        make_response('item not found', 404)

    # handling GET request
    if request.method == 'GET':
        # checking for login
        if is_login() is False:
            # return auth access error
            return make_response('unauthorized access', 401)
        # checking for authorization
        if item.user_id != login_session['user_id']:
            # return auth access error
            return make_response('unauthorized access', 401)
        return render_template('edit_item.html',
                               categories=CATEGORIES, item=item)
    # handling post request
    else:
        # checking for login
        if is_login() is False:
            # return auth access error
            return make_response('unauthorized access', 401)

        # checking for authorization
        if item.user_id != login_session['user_id']:
            # return auth access error
            return make_response('unauthorized access', 401)

        # user is logged in
        # extracting form entries
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']

        # updating item
        # if update is successful updated is True else False
        updated = database.edit_item(item=item, name=name,
                                     description=description,
                                     category=category)
        #  checking item updated or not
        if updated is True:
            flash('item updated')
        else:
            flash('item name already exist. Please change item name')

        # redirecting user to item page
        return redirect(url_for('show_items', category=category))


# This method will delete particular item from our catalog application
# item (variable in url): defines particular item stored in our database
@app.route('/catalog/<string:item>/delete/', methods=['GET', 'POST'])
def delete_item(item):
    # getting item from database
    item = database.get_item(name=item)

    # if item not found
    if item is None:
        make_response('item not found', 404)
    # handling GET request
    if request.method == 'GET':
        # checking for login
        if is_login() is False:
            # return auth access error
            return make_response('unauthorized access', 401)
        # checking for authorization
        if item.user_id != login_session['user_id']:
            # return auth access error
            return make_response('unauthorized access', 401)
        return render_template('delete_item.html', item=item)
    # handling post request
    else:
        # checking for login
        if is_login() is False:
            # return auth access error
            return make_response('unauthorized access', 401)

        # checking for authorization
        if item.user_id != login_session['user_id']:
            # return auth access error
            return make_response('unauthorized access', 401)

        # deleting item
        database.delete_item(item.name)

        # setting flash msg
        flash('item deleted')

        # redirect to home page
        return redirect('/')


# this method will exchange short term google oauth access token for long term
# access token and set user's login details
# This method only support post request
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # check state token
    if request.args.get('state') != login_session['session']:
        response = make_response(json.dumps("INVALID TOKEN"), 401)
        response.headers["Content-Type"] = 'application/json'
        return response

    # state token is correct
    # storing code from client

    code = request.data

    # trying to get object containing access token for server
    # via exchanging one time code provided by client
    try:
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code=code)
    except FlowExchangeError:
        # sending flow exchange error
        response = make_response(json.dumps('unable to upgrade authorization '
                                            'code'), 401)
        response.headers["Content-Type"] = 'application/json'
        return response

    # checking that access token is valid or not
    access_token = credentials.access_token
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?' \
          'access_token={}'.format(access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode())

    # checking if result contain error or not
    if result.get("error") is not None:
        response = make_response(json.dumps(result.get('error')), 501)
        print('server error')
        response.headers['Content-Type'] = 'application/json'
        return response

    # now we have valid access token
    # checking that user id is same as requested or not
    gp_id = credentials.id_token['sub']
    if result['user_id'] != gp_id:
        response = make_response(json.dumps('token user id does not match'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # user id matched
    # checking client id
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps('token user id does not match'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # checking user already logged in or not
    stored_credentials = login_session.get('credentials', None)
    stored_gplus_id = login_session.get('gplus_id', None)
    if stored_credentials is not None and stored_gplus_id is not None:
        response = make_response(json.dumps('user already logged in'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gp_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # storing user info in our session for later use
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # check if user already exist in our database
    if database.check_id(email=login_session['email']) is True:
        # user exist so we are getting user id
        login_session['user_id'] = database.get_user(login_session['email']).id
    else:
        # user does not exist
        # so we create user in our database and store user id
        login_session['user_id'] = database.add_user(
            name=login_session['username'],
            email=login_session[
                'email'],
            picture=login_session[
                'picture']).id
    # add flash msg functionality here
    flash('Welcome {}'.format(login_session['username']))

    response = make_response(json.dumps('user logged in'), 200)
    return response


# This method disconnects user google acc and make that access token invalid
@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
    access_token = login_session.get('access_token', None)
    # if true currently no user connected
    if access_token is None:
        response = make_response(json.dumps("No user connected"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # logging out user
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(
        access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # deleting user data stored in session
        del login_session['access_token']
        del login_session['user_id']
        del login_session['username']
        del login_session['picture']
        del login_session['gplus_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('user logged out')
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# API end point to get list of all items of particular category
@app.route('/catalog/<string:item_cat>/JSON')
def get_items_json(item_cat):
    """returns list of items belonging to requested category in json format
    @:parameter item_cat: item category
    """
    items = database.get_items(item_cat)
    return jsonify(Items=[i.serialize for i in items])


# This methods check if user is logged in or not
# returns True if user is logged in
# returns False in vice versa condition
def is_login():
    if login_session.get('user_id', None) is not None and \
                    login_session.get('access_token', None) is not None:
        print(login_session['username'])
        return True
    else:
        return False


# This method generates CSRF token for protection against CSRF
def generate_csrf_token():
    if '_csrf_token' not in login_session:
        login_session['_csrf_token'] = ''.join(
            random.choice(string.ascii_lowercase +
                          string.ascii_uppercase +
                          string.digits) for _ in range(32))
    return login_session['_csrf_token']


# adding app variables
app.jinja_env.globals['csrf_token'] = generate_csrf_token
app.secret_key = 'super_secret_key'

# will run this part of code only when this file is executed directly
# will not run if this file is imported to another module/script
if __name__ == '__main__':
    port = 5000  # setting port no to listen request
    host = '0.0.0.0'  # setting host address
    app.debug = True
    print(' server is running @ {}:{}'.format(host, port))
    app.run(host=host, port=port)  # making our server online
