import ldap
from flask import flash
from flask_login import LoginManager, login_required, UserMixin
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired, Length
from frontend import app
from backend.libvirtbridge import DomainQuery
import config as cfg

class User(UserMixin):
    users = []

    def __init__(self, username, password):
        self.displayname = ''
        self.username = username
        self.id = 0
        self.userdata = {}

    def try_login(username, password):
            auth_mode = cfg.auth['auth_mode']
            if auth_mode == 'ldap':
                    conn = ldap.initialize(cfg.auth['LDAP_PROVIDER_URL'])
                    if conn is None:
                        flash('error connecting to LDAP server')
                    else:
                        DomainQuery.log('authentication options: certfile: %s, user=%s, password=%s, search base=%s' % (cfg.auth['LDAP_CACERT'], username, password, cfg.auth['LDAP_SEARCH_BASE']))
                        conn.set_option(ldap.OPT_X_TLS, True)
                        conn.set_option(ldap.OPT_X_TLS_CACERTFILE, cfg.auth['LDAP_CACERT'])
                        conn.simple_bind_s('%s' % (cfg.auth['LDAP_BIND_DN']), cfg.auth['LDAP_AUTHTOK'])
                        #conn.simple_bind_s('uid=%s,%s' % (request.form['username'], cfg.auth['LDAP_BIND_DN']), request.form['password'])

                        # do a search
                        query = 'uid=%s' % username
                        #result = conn.search_s(cfg.auth['LDAP_SEARCH_BASE'], ldap.SCOPE_SUBTREE, query)
                        #DomainQuery.log('result = [%s]' % result)
                        #if result:
                        #    self.userdata = result[0][1]
                        #    self.displayname = self.userdata['cn'][0].decode('utf-8')
                        #else:
                        #    flash('authentication error')
                        #    return False

            elif auth_mode == 'plain':
                if password == cfg.auth['default_password'] and username == cfg.auth['default_user']:
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
        return displayname

    def get_id(user_id):
        return id

class LoginForm(FlaskForm):
    username = TextField('login_user',  validators=[InputRequired(),  Length(max=30)])
    password = PasswordField('login_pass', validators=[InputRequired(), Length(min=8, max=20)])
    username.label = 'Usuário'
    password.label = 'Senha'
    
