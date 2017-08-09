from flask import (
    Blueprint, render_template, redirect, request,
    make_response, flash, jsonify)
from database_setup import Base, Catalog, User, Item
from model import session
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import requests
import json
import httplib2

user = Blueprint('user', __name__, template_folder='templates')

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


@user.route('/login')
def showLogin():
    """
    A route to login using facebook or google account
    """
    state = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@user.route('/gconnect', methods=['POST'])
def gconnect():
    """
    LOGIN BY CONNECT TO GOOGLE
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'POST')[1])
    error = result.get('error')

    if error is not None:
        response = make_response(json.dumps(error), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps('Token user ID does not match given user ID.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('plus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'

    # If none of if statements above were true,
    # the user of the current session successfully connects the app with Google
    # Store new credentials and gplus id to the session for return users
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    login_session['provider'] = 'google'

    # Then get user info by providing access token to Google API
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    # Store the detail data
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    # Create a new User record if non-existed user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;" \
    "-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


@user.route('/fbconnect', methods=['POST'])
def fbconnect():
    """
    LOGIN BY CONNECT TO FACEBOOK
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application'
        return response
    access_token = request.data

    # Exchange client token for long-lived server-side token
    app_id = json.loads(open(
        'fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open(
        'fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/v2.8/oauth/" \
    "access_token?grant_type=fb_exchange_token" \
    "&client_id=%s&client_secret=%s&fb_exchange_token=%s' \
    % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # Use token to get user info from API
    data = json.loads(result)
    token = 'access_token=' + data['access_token']

    url = 'https://graph.facebook.com/v2.8/me?%s&fields=name,id,email' \
        % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    if "error" in result:
        response = make_response(json.dumps('Fail to request data'), 401)
        response.headers['Content-Type'] = 'application'
        return response

    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    login_session['credentials'] = token

    # Retrieve user profile picture
    url = 'https://graph.facebook.com/v2.8/me/picture?%s&redirect=0" \
    "&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # Create a new User record if non-existed user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;" \
    "-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


@user.route('/disconnect')
def disconnect():
    """
    A route to log out, delete currest browser session
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            result = gdisconnect()
            if result['status'] != '200':
                response = make_response(
                    json.dumps('Failed to revoke token for given user.'), 400)
                response.headers['Content-Type'] = 'application/json'
                return response
            del login_session['gplus_id']

        if login_session['provider'] == 'facebook':
            result = fbdisconnect()
            if result['success'] is False:
                response = make_response(
                    json.dumps('Failed to revoke token for given user.'), 400)
                response.headers['Content-Type'] = 'application/json'
                return response
            del login_session['facebook_id']

        del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        return redirect('/catalogs')


def gdisconnect():
    """
    LOGOUT BY DISCONNECT TO GOOGLE
    """
    # Detect the user is connected
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('You were already signed out.'), 401)
        respnse.headers['Content-Type'] = 'application/json'
        return response
    # To log out, execute HTTP GET request to revoke current token
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    return result


def fbdisconnect():
    """
    LOGOUT BY DISCONNECT TO FACEBOOK
    """
    facebook_id = login_session['facebook_id']
    access_token = login_session['credentials']
    url = 'https://graph.facebook.com/%s/permissions?%s' \
        % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    result = json.loads(result)
    return result


def getUserID(email):
    """
    Find and return user object using email
    """
    try:
        user = session.query(User).filter_by(email=email).one_or_none()
        if user is None:
            flash("This account does not exist.")
            return redirect(url_for('catalog.showAllCatalogs'))

        return user.id
    except:
        return None


def getUserInfo(user_id):
    """
    Find and return user object using user id
    """
    user = session.query(User).filter_by(id=user_id).one_or_none()
    if user is None:
            flash("This account does not exist.")
            return redirect(url_for('catalog.showAllCatalogs'))
    return user


def createUser(login_session):
    """
    Create new user object and return the user id
    """
    newUser = User(
        username=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(
        email=login_session['email']).one_or_none()
    if user is None:
            flash("This account/email does not exist.")
            return redirect(url_for('catalog.showAllCatalogs'))
    return user.id
