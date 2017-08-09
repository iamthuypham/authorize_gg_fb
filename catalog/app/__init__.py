from flask import Flask
from app.user.controllers import user
from app.catalog.controllers import catalog
from app.item.controllers import item
from app.api.controllers import api

app = Flask(__name__)

"""Register User, Catalog, Item, Api blueprint"""
app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(catalog, url_prefix='/catalogs')
app.register_blueprint(item)
app.register_blueprint(api, url_prefix='/api')
