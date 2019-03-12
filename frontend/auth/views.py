import ldap
from flask import request, render_template, flash, redirect, url_for, Blueprint, g, jsonify,  session, abort
from flask_login import current_user, login_user, logout_user, login_required
from frontend import db, login_manager
from frontend.auth.models import User, LoginForm
import os
import json
import gettext
from datetime import datetime
from pprint import pprint
from backend.libvirtbridge import DomainQuery
import config as cfg

auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(id):
    return User.get_id(int(id))

@auth.before_request
def get_current_user():
    g.user = current_user

@auth.route('/')
@auth.route('/home')
@login_required
def home():
    DomainQuery.log('cheguei 1')
    d = DomainQuery()
    DomainQuery.log('cheguei 2')
    domain_db = d.get_data()
    DomainQuery.log('cheguei 3')

    lastUpdated = datetime.strftime(datetime.now(), 'atualizado em %d-%m-%Y %H:%M:%S %p')
    return render_template('home.html', domain_data=domain_db, timestamp=lastUpdated)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('auth.home'))

    form = LoginForm()

    if request.method == 'POST' and form.validate():
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            User.try_login(username, password)
        except ldap.INVALID_CREDENTIALS:
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('login.html', form=form)

        user = User.query.filter_by(username=username).first()

        if not user:
            user = User(username, password)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash('You have successfully logged in.', 'success')
        return redirect(url_for('auth.home'))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('login.html', form=form)


@auth.route('/startvm')
def startvm():
    dom = DomainQuery()
    domain_db = dom.get_data()
    vm_name = request.args.get('name')
    if vm_name is None:
        return render_template('startvm.html', error='VM not specified')
    else:
        DomainQuery.log('VM %s is turned off, turning it on' % vm_name)
        for d in domain_db:
            #DomainQuery.log('domain: %s' % str(d))
            if d['name'] == vm_name:
                DomainQuery.log('create() = %d' % d['object'].create())
        return render_template('startvm.html', error='%s started' % vm_name)

@auth.route('/restartvm')
def restartvm():
    dom = DomainQuery()
    domain_db = dom.get_data()
    vm_name = request.args.get('name')
    if vm_name is None:
        return render_template('restartvm.html', error='VM not specified')
    else:
        DomainQuery.log('Restarting VM: %s' % vm_name)
        for d in domain_db:
            #DomainQuery.log('domain: %s' % str(d))
            if d['name'] == vm_name:
                DomainQuery.log('reset() = %d' % d['object'].reset())
        return render_template('restartvm.html', error='%s reset' % vm_name)





