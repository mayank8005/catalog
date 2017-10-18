from flask import Flask, request, make_response, render_template
from flask import session as login_session
import random
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

CLIENT_ID = json.loads(open("client_secret.json").read())['web']['client_id']

# init Flask instance
app = Flask(__name__)


# it init session variable when client is first connected
@app.before_request
def start_session():
    if login_session.get('session', None) is None:
        login_session['session'] = ''.join(
            random.choice(string.ascii_lowercase +
                          string.ascii_uppercase +
                          string.digits) for _ in range(32))


# home/main page of our catalog application
# can also accessed via '/index'
@app.route('/')
@app.route('/index')
def index():
    login = is_login()
    session_state = login_session['session']
    if login is True:
        return render_template('index.html', STATE=session_state)
    else:
        return render_template('public_index.html', STATE=session_state)


# display's items belonging to one of the categories
# category (variables in url): specifies category
@app.route('/catalog/<string:category>/items/')
def show_items(category):
    return 'showing items from ' + category + ' category'


# display's more info about particular item in the list
# category (variable in url): defines particular category
# item (variable in url): defines particular item
@app.route('/catalog/<string:category>/<string:item>/')
def show_item(category, item):
    return 'showing ' + item + ' which belongs to ' + category


# adds item in our catalog application
@app.route('/catalog/add/')
def add_item():
    return 'will add items'


# This method will edit particular item of our catalog application
# item (variable in url): defines particular item stored in our database
@app.route('/catalog/<string:item>/edit/')
def edit_item(item):
    return 'edit item: ' + item


# This method will delete particular item from our catalog application
# item (variable in url): defines particular item stored in our database
@app.route('/catalog/<string:item>/delete/')
def delete_item(item):
    return 'delete item: ' + item


# this method will exchange short term google oauth access token for long term
# access token
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

    # TODO: add user table database action here

    # TODO: add flash msh functionality here

    response = make_response(json.dumps('user logged in'), 200)
    return response


# This methods check if user is logged in or not
# returns True if user is logged in
# returns False in vice versa condition
def is_login():
    if login_session.get('username', None) is not None:
        return True
    else:
        return False


# will run this part of code only when this file is executed directly
# will not run if this file is imported to another module/script
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    port = 5000  # setting port no to listen request
    host = '0.0.0.0'  # setting host address
    app.debug = True
    print(' server is running @ {}:{}'.format(host, port))
    app.run(host=host, port=port)  # making our server online
