import os
import urllib2
import unicodedata
import httplib
import json
import subprocess
from copy import deepcopy
from datetime import datetime

from flask import Flask, jsonify, json, request, redirect, abort, make_response
from flask import render_template, flash
from flask.views import View, MethodView
from flask.ext.login import login_user, current_user

import bibserver.dao
import bibserver.util as util
import bibserver.importer
import bibserver.ingest
from bibserver.config import config
from bibserver.core import app, login_manager
from bibserver.view.account import blueprint as account
from bibserver import auth

import logging
from logging.handlers import RotatingFileHandler

LOG_FILENAME="logs/app.log"
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(
   "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
handler = RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=5)
handler.setFormatter(formatter)
log.addHandler(handler)

#app.register_blueprint(account, url_prefix='/account')


@app.route('/')
def home():
    log.debug("Hommmme!")
    data = []
    try:
        colldata = bibserver.dao.Collection.query(sort={"_created.exact":{"order":"desc"}},size=20)
        if colldata['hits']['total'] != 0:
            for coll in colldata['hits']['hits']:
                colln = bibserver.dao.Collection.get(coll['_id'])
                if colln:
                    data.append({
                        'name': colln['label'], 
                        'records': len(colln), 
                        'owner': colln['owner'], 
                        'slug': colln['collection'],
                        'description': colln['description']
                    })
    except:
        pass
    colls = bibserver.dao.Collection.query().total
    records = bibserver.dao.Record.query().total
    users = bibserver.dao.Account.query().total
    log.debug(colls)
    log.debug(records)
    log.debug(users)

    print data
    return render_template('home/index.html', colldata=json.dumps(data), colls=colls, records=records, users=users)

if __name__ == "__main__":
    log.debug("Start....")
    if config["allow_upload"]:
        bibserver.ingest.init()
        if not os.path.exists('ingest.pid'):
            ingest=subprocess.Popen(['python', 'bibserver/ingest.py'])
            open('ingest.pid', 'w').write('%s' % ingest.pid)
    try:
        bibserver.dao.init_db()
        app.run(host='0.0.0.0', debug=config['debug'], port=config['port'])
    finally:
        if os.path.exists('ingest.pid'):
            os.remove('ingest.pid')
