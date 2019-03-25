import ldap
from flask import flash
from flask_login import LoginManager, login_required, UserMixin
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired, Length
from backend.libvirtbridge import DomainQuery
from frontend import app, db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=True)
    username = db.Column(db.String(100))
    displayname = db.Column(db.String(100))
    last_ip = db.Column(db.String(50))

    def __init__(self, username, password):
        self.username = username

    @staticmethod
    def try_login(username, password):
            if app.config['auth_mode'] == 'ldap':
                    conn = ldap.initialize(app.config['LDAP_PROVIDER_URL'])
                    if conn is None:
                        flash('error connecting to LDAP server')
                    else:
                        DomainQuery.log('authentication options: certfile: %s, user=%s, password=%s, search base=%s' % (app.config['LDAP_CACERT'], username, password, app.config['LDAP_SEARCH_BASE']))
                        conn.set_option(ldap.OPT_X_TLS, True)
                        if app.config['LDAP_CACERT'] != '':
                            conn.set_option(ldap.OPT_X_TLS_CACERTFILE, app.config['LDAP_CACERT'])
                        conn.simple_bind_s('%s,%s' % (app.config['LDAP_BIND_USER'], app.config['LDAP_BIND_DN']), app.config['LDAP_AUTHTOK'])
                        #conn.simple_bind_s('uid=%s,%s' % (username, app.config['LDAP_BIND_DN']), password)

                        # do a search
                        query = 'uid=%s' % username
                        result = conn.search_s(app.config['LDAP_SEARCH_BASE'], ldap.SCOPE_SUBTREE, query)
                        DomainQuery.log('result = [%s]' % result)
                        if result:
                            userdata = result[0][1]
                            displayname  = userdata['cn'][0].decode('utf-8')
                            return (True, displayname, userdata)
                        else:
                            flash('authentication error')
                            return (False, '', {})

            elif app.config['auth_mode'] == 'plain':
                if password == app.config['default_password'] and username == app.config['default_user']:
                    displayname = app.config['default_user']
                    return  (True, displayname, {})
                    
            return (False, '', {})

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_displayname(self):
        return self.displayname

    def set_displayname(self, new_displayname):
        self.displayname = new_displayname
        return True

    def get_id(self):
        return self.id

    def set_id(self, new_id):
        self.id = new_id
        return True

    def get_last_ip(self):
        return self.last_ip

    def set_last_ip(self, new_last_ip):
        self.last_ip = new_last_ip
        return True

class LoginForm(FlaskForm):
    username = TextField('login_user',  validators=[InputRequired(),  Length(max=30)])
    password = PasswordField('login_pass', validators=[InputRequired(), Length(min=8, max=20)])
    
