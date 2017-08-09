from flask import (
    Blueprint, render_template, redirect, request, url_for, flash, jsonify)
from database_setup import Base, Catalog, User, Item
from model import session
from flask import session as login_session

api = Blueprint('api', __name__)


# A route for JSON API Endpoint (GET Request)
@api.route('/catalogs/<int:id>/', methods=['GET', 'PUT', 'DELETE'])
def showAllCatalogsJSON(id):
    if request.method == 'GET':
        catalogs = session.query(Catalog).all()
        return jsonify(Catalogs=[i.serialize for i in catalogs])
