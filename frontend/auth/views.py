import ldap
from flask import request, render_template, flash, redirect, url_for, Blueprint, g, jsonify,  session, abort
from flask_login import current_user, login_user, logout_user, login_required
from frontend import app, db, login_manager
from frontend.auth.models import User, LoginForm
import os
import json
import gettext
from datetime import datetime
from pprint import pprint
from backend.libvirtbridge import DomainQuery
from backend.utils import process_exception

auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@auth.before_request
def get_current_user():
    g.user = current_user

@auth.route('/')
@auth.route('/home')
@login_required
def home():
    try:
        d = DomainQuery()
        domain_db = d.get_data()
    except Exception as e:
        return render_template('error.html', errorinfo=process_exception(e))

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
            displayname = ''
            userdata = {}
            authenticated = False
            authenticated, displayname, userdata = User.try_login(username, password)
        except ldap.INVALID_CREDENTIALS:
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('login.html', form=form)

        if not authenticated:
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('login.html', form=form)

        user = User.query.filter_by(username=username).first()
        
        if user is None:
            user = User(username, password)
            DomainQuery.log('user not found, creating new record: user = %s, id = %s' % (user.username, user.id))
        else:
            DomainQuery.log('found user record for user %s, id = %s' % (user.displayname, user.id))
      
        user.set_displayname(displayname)
        DomainQuery.log('setting last IP to: %s' % str(request.remote_addr))
        user.set_last_ip(str(request.remote_addr))

        # commit the user record to the database
        db.session.add(user)
        db.session.flush()
        db.session.refresh(user)
        db.session.commit()

        login_user(user, force=True, remember=True)
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



@auth.route('/showerror')
def show_error():
    
    error=process_exception(exception)

    DomainQuery.log('Fatal error: showing error page (%s)' % error['title'])
    return render_template('error.html', errorinfo=error)


