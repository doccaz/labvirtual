import os
import json
from flask import Flask, request, jsonify, render_template, redirect, request
from datetime import datetime
from pprint import pprint
from libvirtdata import DomainQuery
app = Flask(__name__, instance_relative_config=True)

@app.route('/')
def index():

    d = DomainQuery()
    domain_db = d.get_data()

    lastUpdated = datetime.strftime(datetime.now(), 'atualizado em %d-%m-%Y %H:%M %p')
    return render_template('index.html', domain_data=domain_db, timestamp=lastUpdated)


@app.route('/startvm')
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

@app.route('/restartvm')
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
    
    
@app.teardown_appcontext
def shutdown_session(exception=None):
    DomainQuery.close()


if __name__ == '__main__':
    app.run()


