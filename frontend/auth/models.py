import ldap
from flask import flash
from flask_login import LoginManager, login_required, UserMixin
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired, Length
from frontend import db, app
from backend.libvirtbridge import DomainQuery
import config as cfg

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))

    def __init__(self, username, password):
        self.displayname = ''
        self.username = username
        self.id = 0
        self.userdata = {}

    def try_login(username, password):
            auth_mode = cfg.config['auth_mode']
            if auth_mode == 'ldap':
                    conn = ldap.initialize(cfg.config['LDAP_PROVIDER_URL'])
                    if conn is None:
                        flash('error connecting to LDAP server')
                    else:
                        DomainQuery.log('authentication options: certfile: %s, user=%s, password=%s, search base=%s' % (cfg.config['LDAP_CACERT'], username, password, cfg.config['LDAP_SEARCH_BASE']))
                        conn.set_option(ldap.OPT_X_TLS, True)
                        if cfg.config['LDAP_CACERT'] != '':
                            conn.set_option(ldap.OPT_X_TLS_CACERTFILE, cfg.auth['LDAP_CACERT'])
                        conn.simple_bind_s('%s,%s' % (cfg.config['LDAP_BIND_USER'], cfg.config['LDAP_BIND_DN']), cfg.config['LDAP_AUTHTOK'])
                        #conn.simple_bind_s('uid=%s,%s' % (username, cfg.config['LDAP_BIND_DN']), password)

                        # do a search
                        query = 'uid=%s' % username
                        #result = conn.search_s(cfg.config['LDAP_SEARCH_BASE'], ldap.SCOPE_SUBTREE, query)
                        #DomainQuery.log('result = [%s]' % result)
                        #if result:
                        #    self.userdata = result[0][1]
                        #    self.displayname = self.userdata['cn'][0].decode('utf-8')
                        #else:
                        #    flash('authentication error')
                        #    return False

            elif auth_mode == 'plain':
                if password == cfg.config['default_password'] and username == cfg.config['default_user']:
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

    def get_id(self):
        return id

class LoginForm(FlaskForm):
    username = TextField('login_user',  validators=[InputRequired(),  Length(max=30)])
    password = PasswordField('login_pass', validators=[InputRequired(), Length(min=8, max=20)])
    
