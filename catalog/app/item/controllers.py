from flask import (
    Blueprint, render_template, redirect, request, url_for, flash, jsonify)
from database_setup import Base, Catalog, User, Item
from model import session
from flask import session as login_session
from app import decorator

item = Blueprint('item', __name__, template_folder='templates')


@item.route('/catalogs/<int:catalog_id>/items')
@decorator.validate_exist_catalog
def showAllItems(catalog_id):
    """
    A route to display all items of one catalog
    """
    items = session.query(Item).filter_by(catalog_id=catalog_id).all()
    catalog = session.query(Catalog).filter_by(id=catalog_id).one_or_none()
    if catalog is None:
        flash("The catalog you are looking for does not exist.")
        return redirect(url_for('catalog.showAllCatalogs'))

    if 'username' not in login_session:
        return render_template(
            'public_items.html',
            catalog=catalog,
            items=items)
    else:
        return render_template(
            'items.html',
            catalog=catalog,
            session=login_session,
            items=items)


@item.route('/catalogs/<int:catalog_id>/items/new', methods=['GET', 'POST'])
@decorator.login_required
@decorator.validate_exist_catalog
def createNewItem(catalog_id):
    """
    Create new item of one catalog
    """
    catalog = session.query(Catalog).filter_by(id=catalog_id).one_or_none()
    if catalog is None:
        flash("The catalog you are looking for does not exist.")
        return redirect(url_for('catalog.showAllCatalogs'))

    if request.method == 'POST':
        newItem = Item(
            name=request.form['newItemName'],
            description=request.form['newItemDescription'],
            catalog_id=catalog_id,
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("New menu item created!")
        return redirect(url_for(
            'item.showAllItems',
            catalog_id=catalog_id))
    else:
        return render_template('items_new.html', catalog=catalog)


@item.route('/catalogs/<int:catalog_id>/items/<int:item_id>', methods=['GET'])
@decorator.validate_exist_catalog_and_item
def showItem(catalog_id, item_id):
    """
    Display an item
    """
    catalog = session.query(Catalog).filter_by(id=catalog_id).one_or_none()
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    if catalog is None or item is None:
        flash("The catalog and/or item you are looking for does not exist.")
        return redirect(url_for('catalog.showAllCatalogs'))

    return render_template('item.html', catalog=catalog, item=item)


@item.route(
    '/catalogs/<int:catalog_id>/items/<int:item_id>/edit',
    methods=['GET', 'POST'])
@decorator.login_required
@decorator.validate_exist_catalog_and_item
def editItem(catalog_id, item_id):
    """
    Edit an item
    """
    catalog = session.query(Catalog).filter_by(id=catalog_id).one_or_none()
    editItem = session.query(Item).filter_by(id=item_id).one_or_none()
    if catalog is None or item is None:
        flash("The catalog and/or item you are looking for does not exist.")
        return redirect(url_for('catalog.showAllCatalogs'))

    if editItem.user_id != login_session['user_id']:
        flash("You are not authorized to edit.")
        return redirect(url_for('item.showAllItems', catalog_id=catalog.id))

    if editItem != [] and request.method == 'POST':
        editItem.name = request.form['editItemName']
        editItem.description = request.form['editItemDescription']
        session.add(editItem)
        session.commit()
        flash(editItem.name + " is edited!")
        return redirect(url_for('item.showAllItems', catalog_id=catalog_id))
    elif editItem != [] and request.method == 'GET':
        return render_template(
            'items_edit.html',
            catalog=catalog,
            item=editItem)


@item.route(
    '/catalogs/<int:catalog_id>/items/<int:item_id>/delete',
    methods=['GET', 'POST'])
@decorator.login_required
@decorator.validate_exist_catalog_and_item
def deleteItem(catalog_id, item_id):
    """
    Delete an item
    """
    catalog = session.query(Catalog).filter_by(id=catalog_id).one_or_none()
    deleteItem = session.query(Item).filter_by(id=item_id).one_or_none()
    if catalog is None or item is None:
        flash("The catalog and/or you are looking for does not exist.")
        return redirect(url_for('catalog.showAllCatalogs'))

    if deleteItem.user_id != login_session['user_id']:
        flash("You are not authorized to delete.")
        return redirect(url_for('item.showAllItems', catalog_id=catalog.id))

    if deleteItem != [] and request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash(deleteItem.name + " is deleted!")
        return redirect(url_for('item.showAllItems', catalog_id=catalog_id))
    elif deleteItem != [] and request.method == 'GET':
        return render_template(
            'items_delete.html',
            catalog=catalog,
            item=deleteItem)
