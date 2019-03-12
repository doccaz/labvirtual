import ldap
from flask import flash
from flask_login import LoginManager, login_required, UserMixin
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired, Length
from backend.libvirtbridge import DomainQuery
from frontend import app, db

class User(db.Model):
    username = db.Column(db.String(100), primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    displayname = db.Column(db.String(100))
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
                            conn.set_option(ldap.OPT_X_TLS_CACERTFILE, app.auth['LDAP_CACERT'])
                        conn.simple_bind_s('%s,%s' % (app.config['LDAP_BIND_USER'], app.config['LDAP_BIND_DN']), app.config['LDAP_AUTHTOK'])
                        #conn.simple_bind_s('uid=%s,%s' % (username, app.config['LDAP_BIND_DN']), password)

                        # do a search
                        query = 'uid=%s' % username
                        result = conn.search_s(app.config['LDAP_SEARCH_BASE'], ldap.SCOPE_SUBTREE, query)
                        DomainQuery.log('result = [%s]' % result)
                        if result:
                            #self.userdata = result[0][1]
                            self.displayname = self.userdata['cn'][0].decode('utf-8')
                        else:
                            flash('authentication error')
                            return False

            elif app.config['auth_mode'] == 'plain':
                if password == app.config['default_password'] and username == app.config['default_user']:
                    return True
                else:
                    return False

            return True

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_displayname(self):
        return self.displayname

    def set_displayname(new_displayname):
        self.displayname = new_displayname
        return True

    def get_id(self):
        return self.id

    def set_id(new_id):
        self.id = new_id
        return True

    id = property(get_id, set_id)
    displayname = property(get_displayname, set_displayname)

class LoginForm(FlaskForm):
    username = TextField('login_user',  validators=[InputRequired(),  Length(max=30)])
    password = PasswordField('login_pass', validators=[InputRequired(), Length(min=8, max=20)])
    
