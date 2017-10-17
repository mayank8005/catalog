from flask import Flask

# category list storing names of all predefined categories
CATEGORIES = ['Soccer', 'Basketball', 'Baseball', 'Frisbee', 'Snowboarding',
              'Rock Climbing', 'Foosball', 'Skating', 'Hockey']

# init Flask instance
app = Flask(__name__)


# home/main page of our catalog application
# can also accessed via '/index'
@app.route('/')
@app.route('/index')
def index():
    return 'main page'


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


# will run this part of code only when this file is executed directly
# will not run if this file is imported to another module/script
if __name__ == '__main__':
    port = 5000  # setting port no to listen request
    host = '0.0.0.0'  # setting host address
    app.debug = True
    print(' server is running @ {}:{}'.format(host,port))
    app.run(host=host, port=port)   # making our server online
