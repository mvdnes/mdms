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
import document as doclib
import datetime
import dateutil.parser
import uuid as uuidlib
from docopt import docopt
import werkzeug
import logging
from logging.handlers import RotatingFileHandler

app = flask.Flask(__name__)

log_handler = RotatingFileHandler('log/mdms.log', maxBytes=10000, backupCount=3)
log_handler.setLevel(logging.WARNING)
app.logger.addHandler(log_handler)

@app.before_request
def get_versions():
    import platform
    import subprocess

    flask.g.python_version = platform.python_version()
    flask.g.flask_version = flask.__version__
    try:
        flask.g.git_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
    except subprocess.CalledProcessError:
        flask.g.git_hash = "unknown"

def main(argv):
    args = docopt(__doc__, argv = argv)
    app.run(debug=args['--debug'], host='0.0.0.0')

def get_dbfs():
    configuration = config.parse('config.toml')
    db = database.get_instance(configuration)
    fs = filesystem.get_instance(configuration)
    return (db, fs)

@app.errorhandler(404)
def not_found(e = None):
    return flask.render_template("404.html"), 404

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/search")
def search():
    db, _ = get_dbfs()
    result = []
    tags = [tag for tag in flask.request.args.get('tags').split(' ') if tag != '']
    to_raw = flask.request.args.get('to', '')
    from_raw = flask.request.args.get('from', '')

    to_date = datetime.date.max
    if to_raw != '':
        try:
            to_date = dateutil.parser.parse(to_raw).date()
        except ValueError:
            pass
    from_date = datetime.date.min
    if from_raw != '':
        try:
            from_date = dateutil.parser.parse(from_raw).date()
        except ValueError:
            pass

    result = db.search(tags, from_date, to_date)

    search_tags = ' '.join(tags)
    if from_date == datetime.date.min:
        search_from = ''
    else:
        search_from = str(from_date)
    if to_date == datetime.date.max:
        search_to = ''
    else:
        search_to = str(to_date)

    return flask.render_template("search.html",
            results=result,
            search_tags=search_tags,
            search_from=search_from,
            search_to=search_to)

@app.route("/tagless")
def tagless():
    db, _ = get_dbfs()
    result = db.tagless()
    return flask.render_template("search.html",
            results=result)


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
        return "no upload" #TODO
    file = flask.request.files['document']
    filename = werkzeug.secure_filename(file.filename)
    fs.save(uuid, file, filename)

    return flask.redirect(flask.url_for('edit', uuid=str(uuid)), code=303)

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
    db, fs = get_dbfs()
    try:
        uuid = uuidlib.UUID(uuid)
    except ValueError:
        return not_found()
    doc = db.load(uuid)
    if doc is None:
        return not_found()
    files = fs.get(uuid, basename_only=True)

    return flask.render_template("edit.html", doc=doc, files=files)

@app.route("/save/<uuid>", methods=['POST'])
def save(uuid):
    db, fs = get_dbfs()

    if uuid == 'new':
        doc = doclib.Document()
    else:
        try:
            uuid = uuidlib.UUID(uuid)
        except ValueError:
            return not_found()
        doc = db.load(uuid)
        if doc is None:
            return not_found()

    form = flask.request.form
    if 'name' in form and 'extra' in form and 'date' in form:
        try:
            date = dateutil.parser.parse(form['date']).date()
        except ValueError:
            return "Invalid date" #TODO
        doc.name = form['name']
        doc.extra = form['extra']
        doc.document_date = date
        db.save(doc)
    if 'deltag' in form and 'tag' in form:
        tag = form['tag']
        doc.remove_tag(tag)
        db.save(doc)
    if 'addtag' in form and 'tag' in form:
        tag = form['tag']
        doc.add_tag(tag)
        db.save(doc)
    if 'delfile' in form and 'file' in form:
        file = form['file']
        fs.remove(uuid, file)

    return flask.redirect(flask.url_for('edit', uuid=doc.uuid), code=303)

@app.route("/delete/<uuid>", methods=['GET', 'POST'])
def delete(uuid):
    db, fs = get_dbfs()
    try:
        uuid = uuidlib.UUID(uuid)
    except ValueError:
        return not_found()
    doc = db.load(uuid)
    if doc is None:
        return not_found()

    if flask.request.method == 'POST' and 'yes' in flask.request.form:
        db.remove(doc)
        fs.remove_dir(doc.uuid)
        return flask.redirect(flask.url_for('index'), code=303)

    return flask.render_template("delete.html", doc=doc)

@app.route("/create")
def create():
    return flask.render_template("create.html")

@app.route("/tagoverview")
def tagoverview():
    db, _ = get_dbfs()
    tags = db.tagcount()
    return flask.render_template("tagoverview.html", tags=tags)
