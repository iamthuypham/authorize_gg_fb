from flask import url_for, flash, redirect, session as login_session
from functools import wraps
from model import session
from database_setup import Base, Catalog, Item
from sqlalchemy import exists


def login_required(func):
    """
    Validate if user already logged in
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/user/login')
        else:
            return func(*args, **kwargs)
    return wrapper


def validate_exist_catalog(func):
    """
    Validate if catalog exists or not
    """
    @wraps(func)
    def wrapper(catalog_id):
        result = session.query(
            exists().where(Catalog.id == catalog_id)).scalar()
        if result is False:
            flash("The catalog you are looking for does not exist!")
            return redirect(url_for('catalog.showAllCatalogs'))
        else:
            return func(catalog_id)
    return wrapper


def validate_exist_catalog_and_item(func):
    """
    Validate if both catalog and item exists or not
    """
    @wraps(func)
    def wrapper(catalog_id, item_id):
        catalog = session.query(
            exists().where(Catalog.id == catalog_id)).scalar()
        item = session.query(
            exists().where(Item.id == item_id)).scalar()
        if catalog is False or item is False:
            flash(
                "The catalog and/or item you are looking for does not exist!")
            return redirect(url_for('catalog.showAllCatalogs'))
        else:
            return func(catalog_id, item_id)
    return wrapper
