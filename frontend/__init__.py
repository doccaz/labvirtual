from flask import Flask
import os
import flask_login
from flask_sqlalchemy import SQLAlchemy
from backend.libvirtbridge import DomainQuery

# translation support
try:
    import gettext
    gettext.install('labvirtual', '/usr/share/locale')
except FileNotFoundError as e:
    DomainQuery.log("no translation file available")

app = Flask(__name__)
app.secret_key = os.urandom(12)
app.debug = False

# load configuration
import config as cfg
for key, value in cfg.config.items():
    app.config[key] = value

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

db = SQLAlchemy()

from frontend.auth.views import auth
app.register_blueprint(auth)

db.init_app(app)
db.create_session(app)
db.create_all()

@app.teardown_appcontext
def shutdown_session(exception=None):
    DomainQuery.close()

