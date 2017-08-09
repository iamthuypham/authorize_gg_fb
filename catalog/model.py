from database_setup import Base, Catalog, User, Item
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

"""Create database session to make query"""
engine = create_engine('sqlite:///item_catalog_project_with_user.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
