"""
usage: mdms import <file>
"""

from docopt import docopt
import database
import filesystem
import config
import document
import datetime
import json
import uuid as uuidlib
import dateutil.parser

def main(argv):
    args = docopt(__doc__, argv = argv)
    filename = args['<file>']
    db, _ = get_dbfs()

    with open(filename) as file:
        docs = json.load(file)
        for data in docs:
            doc = document.Document(
                    uuid = uuidlib.UUID(data['uuid']),
                    name = data['name'],
                    creation_date = dateutil.parser.parse(data['creation_date']).date(),
                    document_date = dateutil.parser.parse(data['document_date']).date(),
                    tags = data['tags'],
                    extra = data['extra'])
            try:
                db.save(doc)
            except database.ExistsError:
                print(str(doc.uuid) + " already exists")

def get_dbfs():
    configuration = config.parse('config.toml')
    db = database.get_instance(configuration)
    fs = filesystem.get_instance(configuration)
    return (db, fs)
