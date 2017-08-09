from flask import (
 Blueprint, render_template, redirect, request, url_for, flash, jsonify)
from database_setup import Base, Catalog, User, Item
from model import session
from flask import session as login_session
from app import decorator

catalog = Blueprint('catalog', __name__, template_folder='templates')


@catalog.route('/')
def showAllCatalogs():
    """
    A catalogs route to show all catalogs
    """
    catalogs = session.query(Catalog).all()
    if 'username' not in login_session:
        return render_template('public_catalogs.html', catalogs=catalogs)
    else:
        return render_template(
            'catalogs.html',
            catalogs=catalogs,
            session=login_session)


@catalog.route('/new', methods=['GET', 'POST'])
@decorator.login_required
def createNewCatalog():
    """
    A new route to create a new catalogs
    """
    if request.method == 'POST':
        newCatalog = Catalog(
            name=request.form['newCatalogName'],
            user_id=login_session['user_id'])
        session.add(newCatalog)
        session.commit()
        flash("New menu item created!")
        return redirect(url_for('catalog.showAllCatalogs'))
    else:
        return render_template('catalogs_new.html')


@catalog.route('/<int:catalog_id>/edit', methods=['GET', 'POST'])
@decorator.login_required
@decorator.validate_exist_catalog
def editCatalog(catalog_id):
    """
    A route to edit a specific catalog
    """
    editCatalog = session.query(Catalog).filter_by(id=catalog_id).one_or_none()
    if editCatalog is None:
        flash("The catalog you are looking for does not exist.")
        return redirect(url_for('catalog.showAllCatalogs'))
    if editCatalog.user_id != login_session['user_id']:
        flash("You are not authorized to edit.")
        return redirect(url_for('catalog.showAllCatalogs'))
    if editCatalog != [] and request.method == 'POST':
        editCatalog.name = request.form['editCatalogName']
        session.add(editCatalog)
        session.commit()
        flash(editCatalog.name + " is edited!")
        return redirect(url_for('catalog.showAllCatalogs'))
    elif editCatalog != [] and request.method == 'GET':
        return render_template('catalogs_edit.html', catalog=editCatalog)


@catalog.route('/<int:catalog_id>/delete', methods=['GET', 'POST'])
@decorator.login_required
@decorator.validate_exist_catalog
def deleteCatalog(catalog_id):
    """
    A route to delete a specific catalogs
    """
    deleteCatalog = session.query(
        Catalog).filter_by(id=catalog_id).one_or_none()
    if deleteCatalog is None:
        flash("The catalog you are looking for does not exist.")
        return redirect(url_for('catalog.showAllCatalogs'))
    if deleteCatalog.user_id != login_session['user_id']:
        flash("You are not authorized to delete.")
        return redirect(url_for('catalog.showAllCatalogs'))
    if deleteCatalog != [] and request.method == 'POST':
        session.delete(deleteCatalog)
        session.commit()
        flash(deleteCatalog.name + " is deleted!")
        return redirect(url_for('catalog.showAllCatalogs'))
    elif deleteCatalog != [] and request.method == 'GET':
        return render_template('catalogs_delete.html', catalog=deleteCatalog)
