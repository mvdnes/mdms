"""
usage: mdms web [--debug]

options:
    --debug, -d     debug mode
"""

import flask
from flask import Flask
import config
import database
import filesystem
import datetime
import uuid as uuidlib
from docopt import docopt

app = Flask(__name__)

def main(argv):
    args = docopt(__doc__, argv = argv)
    app.run(debug=args['--debug'])

def get_dbfs():
    configuration = config.parse('config.toml')
    db = database.get_instance(configuration)
    fs = filesystem.get_instance(configuration)
    return (db, fs)

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/search")
def search():
    db, fs = get_dbfs()
    result = []
    tags = flask.request.args.get('tags').split(' ')
    if len(tags) != 0:
        result = db.search(tags, datetime.datetime.min, datetime.datetime.max)
    return flask.render_template("search.html", results=result)

@app.route("/document/<uuid>")
def document(uuid):
    db, fs = get_dbfs()
    try:
        uuid = uuidlib.UUID(uuid)
    except ValueError:
        return "invalid UUID" # TODO
    doc = db.load(uuid)
    if doc is None:
        return "not found" # TODO
    files = fs.get(uuid, basename_only=True)
    return flask.render_template("document.html", doc=doc, files=files)

@app.route("/download/<uuid>/<file>")
def download(uuid, file):
    _, fs = get_dbfs()
    try:
        uuid = uuidlib.UUID(uuid)
    except ValueError:
        return "not found" #TODO
    path = fs.get(uuid, file=file)
    if path is None:
        return "not found" # TODO
    return flask.send_from_directory("data/" + str(uuid) + "/", file)
