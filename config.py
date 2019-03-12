config = {}
# may be 'plain' or 'ldap'
config['auth_mode'] = 'plain'
config['default_user'] = 'admin'
config['default_password'] = 'password'
config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/labvirtual.db'
config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# LDAP
config['LDAP_PROVIDER_URL'] = ''
config['LDAP_BIND_USER'] = ''
config['LDAP_BIND_DN'] = ''
config['LDAP_AUTHTOK'] = ''
config['LDAP_SEARCH_BASE'] = ''
config['LDAP_CACERT'] = ''

