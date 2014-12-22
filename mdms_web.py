"""
usage: mdms web [--debug]

options:
    --debug, -d     debug mode
"""

import os
import flask
import config
import database
import filesystem
import datetime
import uuid as uuidlib
from docopt import docopt
import werkzeug

app = flask.Flask(__name__)

def main(argv):
    args = docopt(__doc__, argv = argv)
    app.run(debug=args['--debug'])

def get_dbfs():
    configuration = config.parse('config.toml')
    db = database.get_instance(configuration)
    fs = filesystem.get_instance(configuration)
    return (db, fs)

def not_found():
    return flask.render_template("404.html"), 404

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/search")
def search():
    db, _ = get_dbfs()
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
        return not_found()
    doc = db.load(uuid)
    if doc is None:
        return not_found()
    files = fs.get(uuid, basename_only=True)
    return flask.render_template("document.html", doc=doc, files=files)

@app.route("/upload/<uuid>", methods=['POST'])
def upload(uuid):
    _, fs = get_dbfs()
    try:
        uuid = uuidlib.UUID(uuid)
    except ValueError:
        return not_found()

    if 'document' not in flask.request.files:
        return "no upload"
    file = flask.request.files['document']
    filename = werkzeug.secure_filename(file.filename)
    fs.save(uuid, file, filename)

    return flask.redirect(flask.url_for('document', uuid=str(uuid)), code=303)

@app.route("/download/<uuid>/<file>")
def download(uuid, file):
    _, fs = get_dbfs()
    try:
        uuid = uuidlib.UUID(uuid)
    except ValueError:
        return not_found()
    path = fs.get(uuid, file=file)
    if path is None:
        return not_found()

    return flask.send_from_directory(fs.get_dir(uuid), file, as_attachment = True)

@app.route("/edit/<uuid>")
def edit(uuid):
    pass
