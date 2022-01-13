# labvirtual
KVM web frontend based on Flask


## installation steps

1. Clone the project inside /srv/www. You should now have /srv/www/labvirtual. Set the owner to wwwrun (or the equivalent daemon user in your distro).

2. Edit config.py to reflect your authentication preferences. Here's an example using LDAP:
```
config = {}
# may be 'plain' or 'ldap'
config['auth_mode'] = 'ldap'
config['default_user'] = 'admin'
config['default_password'] = 'virtuallab'
config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/labvirtual.db'
config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# LDAP
config['LDAP_PROVIDER_URL'] = 'ldaps://myldapserver:636'
config['LDAP_BIND_USER'] = 'uid=mybinduser'
config['LDAP_BIND_DN'] = 'ou=bind,ou=users,O=MYCOMPANY,C=BR'
config['LDAP_AUTHTOK'] = 'mybindpassword'
config['LDAP_SEARCH_BASE'] = 'ou=users,o=MYCOMPANY,c=BR'
config['LDAP_CACERT'] = '/etc/pki/trust/anchors/myCACERT.pem'
``` 

If you're not using LDAP, just set the auth_mode to "plain" and use the default user and password.

3. Install required packages

```
# zypper in -t pattern kvm_server
# zypper in apache2 python3-Flask python3-Flask-Login python3-Flask-SQLAlchemy apache2-mod_wsgi-python3 python3-lxml python3-ldap python3-Flask-WTF python3-websockify libvirt-client
```

(this is for SUSE-based distros. Use your equivalent packages.)

4. Configure the boot services and firewall

```
# systemctl enable firewalld
# systemctl start firewallld
# firewall-cmd --add-service=http
# firewall-cmd --add-service=https
# firewall-cmd --add-service=sshd
# firewall-cmd --runtime-to-permanent
# systemctl enable apache2
# systemctl start apache2
```

5. Include the QEMU hook to allow for automatic firewall rule creation (and websocket redirects!)
```
# cp qemu-hook-script-python /etc/libvirt/hooks/qemu
```

You can find this script here: https://github.com/doccaz/kvm-scripts

Note that this script will create websocket redirects based on what it can find from the VM details. For example, if there is SPICE device (should be default), it'll start a local websocket server that listens on TCP port <SPICE port defined in the VM> + 20000. If it finds a VNC device defined in the VM, it'll start a websocket server on local TCP port <VNC port defined in the VM> + 10000. These will auto-generate "spice console" and "vnc console" buttons in the WebUI, and automatically add the proper iptables rules on the host. Clicking on these buttons will bring up a web-based client to access the VM's console. These are based on the noVNC and spice-web projects.

This is what the WebUI looks like:
  
  ![image](https://user-images.githubusercontent.com/18707695/149360928-b4eb74b5-b7a5-4ffd-94d1-9c13e0fb1577.png)

  
6. Add the wwwrun user to the "libvirt" group with "vigr". Just add "wwwrun" to the end of the respective line.
(or use the equivalent HTTP daemon user for your distro)

7. Access http://<server>/labvirtual
  
  
I recommend you create the VMs with virt-manager. The VMs will show up in the webui and give some basic controls for the user.
  
