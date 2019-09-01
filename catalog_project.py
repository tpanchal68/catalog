from flask import Flask, render_template
from flask import request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Catalog, Base, DishName
from database_setup import User, RecipeIngredients, RecipeMethod
from flask import session as login_session
import random
import string

# Imports for this step
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import os

__author__ = 'tpanchal'
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
print("basedir: {}".format(basedir))
# Connect to Database and create database session
engine = create_engine('sqlite:///' + os.path.join(basedir, 'recipecatalog.db'),
                       connect_args={'check_same_thread': False},
                       echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# ClientId
sec_json_path = os.path.join(basedir, 'client_secrets.json')
CLIENT_ID = json.loads(
    open(sec_json_path, 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

html_alert = """
<script type="text/javascript">
    function alertFunction() {
        alert('Unauthorized.  You are not the owner of this item.');
        window.location.href = "/";
    }
</script>
<body onload='alertFunction()'>
</body>
"""

multiple_user_alert = """
<script type="text/javascript">
    function multiple_user_alertFunction() {
        alert('Cannot Delete.  Multiple users are using this category.');
        window.location.href = "/";
    }
</script>
<body onload='multiple_user_alertFunction()'>
</body>
"""

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    """
    Function renders the login status and allow
    user to login or logout
    :return:
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Function to validate Google connect
    :return: output
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        print("oauth_flow type: {}".format(type(oauth_flow)))
        attrs = vars(oauth_flow)
        print(', '.join("%s: %s\n" % item for item in attrs.items()))
        print("code: {}".format(code))
        credentials = oauth_flow.step2_exchange(code)
        print("Credentials done...")
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    print("access_token: {}".format(credentials.access_token))
    print("gplus_id: {}".format(gplus_id))
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    print("username: {}".format(login_session['username']))
    login_session['picture'] = data['picture']
    # print("picture: {}".format(login_session['picture']))
    login_session['email'] = data['email']
    print("email: {}".format(login_session['email']))

    # see if user exists , if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    print("user_id: {}".format(user_id))
    if not user_id:
        user_id = createUser(login_session)
        print("created user_id: {}".format(user_id))
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' "style = "width: 300px; height: 300px;border-radius: 150px;'\
        '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


def createUser(login_session):
    """
    This function takes information from login_session and
    adds the user in the database if doesn't exist.
    :param login_session:
    :return: user.id
    """
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()

    return user.id


def getUserInfo(user_id):
    """
    This function queries the User table in database and returns the user.
    :param user_id:
    :return: user
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """
    This function queries the User table in database and returns the user id.
    :param email:
    :return: user.id
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        print("user.id: {}".format(user.id))
        return user.id
    except Exception:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    """
    If user is logged in, this function allows user to disconnect.
    :return: response
    """
    access_token = login_session['access_token']
    print("access_token: {}".format(login_session['access_token']))

    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successfully disconnected.")
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/catalog/<int:catalog_id>/dish/<int:dishItems_id>/JSON')
def RecipeJSON(catalog_id, dishItems_id):
    """
    This is command line JSON endpoint that retrieves the
    requested recipe, converts data in JSON format and
    returns to the user.
    :param catalog_id:
    :param dishItems_id:
    :return: serialized json recipe object
    """
    recipeItems = session.query(RecipeIngredients).filter_by(
        dishname_id=dishItems_id).all()
    methodItems = session.query(RecipeMethod).filter_by(
        dishname_id=dishItems_id).all()

    recipeItems = [i.serialize for i in recipeItems]
    methodItems = [i.serialize for i in methodItems]
    data = {'Ingredients': recipeItems, 'Steps': methodItems}

    return jsonify(data)


@app.route('/catalog/<int:catalog_id>/JSON')
def dishNameJSON(catalog_id):
    """
    This is command line JSON endpoint that retrieves all
    available dishes for requested food categories and
    returns to the user.
    :param catalog_id:
    :return: serialized json dish object
    """
    dishItems = session.query(DishName).filter_by(catalog_id=catalog_id).all()
    return jsonify(dishItems=[r.serialize for r in dishItems])


@app.route('/catalog/JSON')
def catalogsJSON():
    """
    This is command line JSON endpoint that retrieves all
    available food catalog (food types) and returns to the user.
    :return: serialized json food category (type) object
    """
    catalogItems = session.query(Catalog).all()
    return jsonify(catalogItems=[r.serialize for r in catalogItems])


# Show homepage
@app.route('/')
@app.route('/catalog')
def showCatalog():
    """
    This is the landing page for the project.  It displays the
    navigation menu as well as all available food categories
    and displays to the users with hyperlink to navigate
    further within the website.
    :return:
    """
    catalogItems = session.query(Catalog).order_by(asc(Catalog.name))
    if ('username' not in login_session):
        return render_template('publiccatalog.html',
                               catalogs=catalogItems,
                               APP_NAME=APPLICATION_NAME)
    else:
        return render_template('catalog.html',
                               catalogs=catalogItems,
                               APP_NAME=APPLICATION_NAME)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalog():
    """
    This function allows user to add new food categories.
    :return:
    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCatalog = Catalog(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCatalog)
        flash('New Catalog Item %s Successfully Created' % newCatalog.name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newcatalog.html')


@app.route('/catalog/<int:catalog_id>/edit/', methods=['GET', 'POST'])
def editCatalog(catalog_id):
    """
    This function retrieves the data for given catalog id,
    validates if login user is the owner of the category,
    and allows user to modify the catalog item.
    :param catalog_id:
    :return:
    """
    catalogToEdit = session.query(
        Catalog).filter_by(id=catalog_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if catalogToEdit.user_id != login_session['user_id']:
        calling_url = '/catalog'
        return html_alert
    if request.method == 'POST':
        if request.form['submit_button'] == 'save':
            if request.form['name']:
                catalogToEdit.name = request.form['name']
                flash('Catalog Item Successfully Edited: {}'.format(
                    catalogToEdit.name))
        return redirect(url_for('showCatalog'))
    else:
        return render_template('editcatalog.html', catalog=catalogToEdit)


@app.route('/catalog/<int:catalog_id>/delete/', methods=['GET', 'POST'])
def deleteCatalog(catalog_id):
    """
    This function retrieves the data for given catalog id,
    validates if login user is the owner of the category,
    and allows user to delete the catalog item.
    :param catalog_id:
    :return:
    """
    catalogToDelete = session.query(
        Catalog).filter_by(id=catalog_id).one()
    print("catalogToDelete: {}".format(catalogToDelete))
    # select DISTINCT user_id from dishname where catalog_id = 1
    dishIds = session.query(
        DishName.user_id.distinct()).filter_by(catalog_id=catalog_id).all()
    print("dishIds: {}".format(dishIds))
    print("len dishIds: {}".format(len(dishIds)))
    if 'username' not in login_session:
        return redirect('/login')
    if catalogToDelete.user_id != login_session['user_id']:
        return html_alert
    if request.method == 'POST':
        if request.form['submit_button'] == 'delete':
            if len(dishIds) == 1:
                session.delete(catalogToDelete)
                session.commit()
                flash('%s Successfully Deleted' % catalogToDelete.name)
            else:
                return multiple_user_alert
        return redirect(url_for('showCatalog', catalog_id=catalog_id))
    else:
        return render_template('deletecatalog.html', catalog=catalogToDelete)


@app.route('/catalog/<int:catalog_id>')
def showDish(catalog_id):
    """
    This function retrieves all available dishes for given catalog id
    and displays to the users.
    :param catalog_id:
    :return:
    """
    catalogItem = session.query(Catalog).filter_by(id=catalog_id).one()
    creator = getUserInfo(catalogItem.user_id)
    dishItems = session.query(DishName).filter_by(catalog_id=catalog_id).all()
    # if ('username' not in login_session or
    #         creator.id != login_session['user_id']):
    if ('username' not in login_session):
        return render_template('publicdish.html',
                               dishItems=dishItems,
                               catalog=catalogItem,
                               creator=creator)
    else:
        return render_template('dish.html',
                               dishItems=dishItems,
                               catalog=catalogItem,
                               creator=creator)


@app.route('/catalog/<int:catalog_id>/dish/new/', methods=['GET', 'POST'])
def newDish(catalog_id):
    """
    This function allows user to add new dish for given catalog id.
    :param catalog_id:
    :return:
    """
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    # if login_session['user_id'] != catalog.user_id:
    #     return html_alert
    if request.method == 'POST':
        newItem = DishName(name=request.form['name'],
                           description=request.form['description'],
                           region=request.form['region'],
                           course=request.form['course'],
                           catalog_id=catalog_id,
                           user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Dish %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showDish', catalog_id=catalog_id))
    else:
        return render_template('newdish.html', catalog_id=catalog_id)


@app.route('/catalog/<int:catalog_id>/dish/<int:dishItems_id>/edit/',
           methods=['GET', 'POST'])
def editDish(catalog_id, dishItems_id):
    """
    This function retrieves the data for given catalog id as well
    as the dish information for given dish item id,
    validates if login user is the owner of the dish,
    and allows user to modify the dish item.
    :param catalog_id:
    :param dishItems_id:
    :return:
    """
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(DishName).filter_by(id=dishItems_id).one()
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if login_session['user_id'] != catalog.user_id:
        return html_alert
    if request.method == 'POST':
        if request.form['submit_button'] == 'save':
            if request.form['name']:
                editedItem.name = request.form['name']
            if request.form['description']:
                editedItem.description = request.form['description']
            if request.form['region']:
                editedItem.region = request.form['region']
            if request.form['course']:
                editedItem.course = request.form['course']
            session.add(editedItem)
            session.commit()
            flash('Dish Item Successfully Edited')
        return redirect(url_for('showDish', catalog_id=catalog_id))
    else:
        return render_template('editdish.html',
                               catalog_id=catalog_id,
                               dishItems_id=dishItems_id,
                               item=editedItem)


@app.route('/catalog/<int:catalog_id>/dish/<int:dishItems_id>/delete/',
           methods=['GET', 'POST'])
def deleteDish(catalog_id, dishItems_id):
    """
    This function retrieves the data for given catalog id as well
    as the dish information for given dish item id,
    validates if login user is the owner of the dish,
    and allows user to delete the dish item.
    :param catalog_id:
    :param dishItems_id:
    :return:
    """
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    itemToDelete = session.query(DishName).filter_by(id=dishItems_id).one()
    if login_session['user_id'] != catalog.user_id:
        return html_alert
    if request.method == 'POST':
        if request.form['submit_button'] == 'delete':
            session.delete(itemToDelete)
            session.commit()
            flash('Item Successfully Deleted')
        return redirect(url_for('showDish', catalog_id=catalog_id))
    else:
        return render_template('deletedish.html',
                               catalog_id=catalog_id,
                               item=itemToDelete)


@app.route('/catalog/<int:catalog_id>/dish/<int:dishItems_id>')
def showRecipe(catalog_id, dishItems_id):
    """
    This function displays the recipe for selected dish.
    :param catalog_id:
    :param dishItems_id:
    :return:
    """
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    creator = getUserInfo(catalog.user_id)
    dishItems = session.query(DishName).filter_by(id=dishItems_id).one()
    recipeItems = session.query(RecipeIngredients).filter_by(
        dishname_id=dishItems_id).all()
    methodItems = session.query(RecipeMethod).filter_by(
        dishname_id=dishItems_id).all()
    if ('username' not in login_session):
        return render_template('publicrecipe.html',
                               dishItems_id=dishItems_id,
                               catalog=catalog,
                               dishItems=dishItems,
                               recipeItems=recipeItems,
                               methodItems=methodItems,
                               creator=creator)
    else:
        return render_template('recipe.html',
                               dishItems_id=dishItems_id,
                               catalog=catalog,
                               dishItems=dishItems,
                               recipeItems=recipeItems,
                               methodItems=methodItems,
                               creator=creator)


@app.route('/catalog/<int:catalog_id>/dish/<int:dishItems_id>/newingredients/',
           methods=['GET', 'POST'])
def newIngredients(catalog_id, dishItems_id):
    """
    This function allows user to add new recipe ingredients for given dish id.
    :param catalog_id:
    :param dishItems_id:
    :return:
    """
    if 'username' not in login_session:
        return redirect('/login')
    dishitem = session.query(DishName).filter_by(id=dishItems_id).one()
    if login_session['user_id'] != dishitem.user_id:
        return html_alert
    if request.method == 'POST':
        newItem = RecipeIngredients(ingredients=request.form['ingredients'],
                                    quantity=request.form['quantity'],
                                    measure=request.form['measure'],
                                    dishname_id=dishItems_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showRecipe',
                                catalog_id=catalog_id,
                                dishItems_id=dishItems_id))
    else:
        return render_template('newingredients.html',
                               catalog_id=catalog_id,
                               dishItems_id=dishItems_id)


@app.route('/catalog/<int:catalog_id>/dish/'
           '<int:dishItems_id>/recipe/<int:recipeItems_id>/edit/',
           methods=['GET', 'POST'])
def editIngredient(catalog_id, dishItems_id, recipeItems_id):
    """
    This function retrieves the ingredient data for given dish item id
    and recipe item id, validates if login user is the owner of the item,
    and allows user to modify the ingredient item.
    :param catalog_id:
    :param dishItems_id:
    :param recipeItems_id:
    :return:
    """
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    editedItem = session.query(RecipeIngredients).filter_by(
        id=recipeItems_id).one()
    if login_session['user_id'] != catalog.user_id:
        return html_alert
    if request.method == 'POST':
        print("request.form['submit_button']: {}".format(
            request.form['submit_button']))
        if request.form['submit_button'] == 'save':
            if request.form['ingredients']:
                editedItem.ingredients = request.form['ingredients']
            if request.form['quantity']:
                editedItem.quantity = request.form['quantity']
            if request.form['measure']:
                editedItem.measure = request.form['measure']
            session.add(editedItem)
            session.commit()
            flash('Dish Item Successfully Edited')
        return redirect(url_for('showRecipe',
                                catalog_id=catalog_id,
                                dishItems_id=dishItems_id))
    else:
        return render_template('editingredients.html',
                               catalog_id=catalog_id,
                               dishItems_id=dishItems_id,
                               recipeItems_id=recipeItems_id,
                               item=editedItem)


@app.route('/catalog/<int:catalog_id>/dish/'
           '<int:dishItems_id>/recipe/<int:recipeItems_id>/delete/',
           methods=['GET', 'POST'])
def deleteIngredient(catalog_id, dishItems_id, recipeItems_id):
    """
    This function retrieves the ingredient data for given dish item id
    and recipe item id, validates if login user is the owner of the item,
    and allows user to delete the ingredient item.
    :param catalog_id:
    :param dishItems_id:
    :param recipeItems_id:
    :return:
    """
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    itemToDelete = session.query(RecipeIngredients).filter_by(
        id=recipeItems_id).one()
    if login_session['user_id'] != catalog.user_id:
        return html_alert
    if request.method == 'POST':
        if request.form['submit_button'] == 'delete':
            session.delete(itemToDelete)
            session.commit()
            flash('Item Successfully Deleted')
        return redirect(url_for('showRecipe',
                                catalog_id=catalog_id,
                                dishItems_id=dishItems_id))
    else:
        return render_template('deleteingredients.html',
                               catalog_id=catalog_id,
                               dishItems_id=dishItems_id,
                               recipeItems_id=recipeItems_id,
                               item=itemToDelete)


@app.route('/catalog/<int:catalog_id>/dish/<int:dishItems_id>/newrecipesteps/',
           methods=['GET', 'POST'])
def newRecipeSteps(catalog_id, dishItems_id):
    """
    This function allows to enter new recipe steps for given dish id.
    :param catalog_id:
    :param dishItems_id:
    :return:
    """
    if 'username' not in login_session:
        return redirect('/login')
    # catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    dishitem = session.query(DishName).filter_by(id=dishItems_id).one()
    if login_session['user_id'] != dishitem.user_id:
        return html_alert
    if request.method == 'POST':
        newItem = RecipeMethod(
            steps=request.form['steps'],
            dishname_id=dishItems_id)
        session.add(newItem)
        session.commit()
        flash('New Dish %s Item Successfully Created' % (newItem.steps))
        return redirect(url_for('showRecipe',
                                catalog_id=catalog_id,
                                dishItems_id=dishItems_id))
    else:
        return render_template('newrecipesteps.html',
                               catalog_id=catalog_id,
                               dishItems_id=dishItems_id)


@app.route('/catalog/<int:catalog_id>/dish/'
           '<int:dishItems_id>/steps/<int:recipeSteps_id>/edit/',
           methods=['GET', 'POST'])
def editRecipeStep(catalog_id, dishItems_id, recipeSteps_id):
    """
    This function retrieves the recipe step data for given dish item id
    and recipe item id, validates if login user is the owner of the item,
    and allows user to modify the recipe step.
    :param catalog_id:
    :param dishItems_id:
    :param recipeSteps_id:
    :return:
    """
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    editedItem = session.query(RecipeMethod).filter_by(id=recipeSteps_id).one()
    if login_session['user_id'] != catalog.user_id:
        return html_alert
    if request.method == 'POST':
        if request.form['submit_button'] == 'save':
            if request.form['steps']:
                editedItem.steps = request.form['steps']
            session.add(editedItem)
            session.commit()
            flash('Dish Item Successfully Edited')
        return redirect(url_for('showRecipe',
                                catalog_id=catalog_id,
                                dishItems_id=dishItems_id))
    else:
        return render_template('editrecipestep.html',
                               catalog_id=catalog_id,
                               dishItems_id=dishItems_id,
                               recipeSteps_id=recipeSteps_id,
                               item=editedItem)


@app.route('/catalog/<int:catalog_id>/dish/'
           '<int:dishItems_id>/steps/<int:recipeSteps_id>/delete/',
           methods=['GET', 'POST'])
def deleteRecipeStep(catalog_id, dishItems_id, recipeSteps_id):
    """
    This function retrieves the recipe step data for given dish item id
    and recipe item id, validates if login user is the owner of the item,
    and allows user to delete the recipe step.
    :param catalog_id:
    :param dishItems_id:
    :param recipeSteps_id:
    :return:
    """
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    itemToDelete = session.query(RecipeMethod).filter_by(
        id=recipeSteps_id).one()
    if login_session['user_id'] != catalog.user_id:
        return html_alert
    if request.method == 'POST':
        if request.form['submit_button'] == 'delete':
            session.delete(itemToDelete)
            session.commit()
            flash('Item Successfully Deleted')
        return redirect(url_for('showRecipe',
                                catalog_id=catalog_id,
                                dishItems_id=dishItems_id))
    else:
        return render_template('deleterecipestep.html',
                               catalog_id=catalog_id,
                               dishItems_id=dishItems_id,
                               recipeItems_id=recipeSteps_id,
                               item=itemToDelete)


@app.route('/about')
def about():
    """
    This function displays what this website is about.
    :return:
    """
    return render_template('about.html')


@app.route('/contact')
def contact():
    """
    This function displays the website contact information to users.
    :return:
    """
    return render_template('contact.html')


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    """
    This function allows user to logout from the website.
    :return:
    """
    print(">>> disconnect...")
    print("login_session: {}".format(login_session))
    gdisconnect()
    del login_session['gplus_id']
    del login_session['access_token']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['state']

    return redirect(url_for('showCatalog'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='localhost', port=8000)
