from flask import Flask
import os
import flask_login
from libvirtdata import DomainQuery

# translation support
try:
    import gettext
    gettext.install('labvirtual', '/usr/share/locale')
except FileNotFoundError as e:
    DomainQuery.log("no translation file available")


#app = Flask(__name__, instance_relative_config=True)
app = Flask(__name__)
app.secret_key = os.urandom(12)
app.debug = False

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

from frontend.auth.views import auth
app.register_blueprint(auth)

@app.teardown_appcontext
def shutdown_session(exception=None):
    DomainQuery.close()

