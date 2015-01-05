"""
usage: mdms export
"""

from docopt import docopt
import database
import filesystem
import config
import datetime
import json

def main(argv):
    args = docopt(__doc__, argv = argv)
    db, _ = get_dbfs()
    docs = db.search([], datetime.datetime.min, datetime.datetime.max)
    res = []
    for doc in docs:
        res.append({
            "uuid": str(doc.uuid),
            "name": doc.name,
            "creation_date": str(doc.creation_date),
            "document_date": str(doc.document_date),
            "tags": list(doc.tags),
            "extra": doc.extra,
        })
    print(json.dumps(res))

def get_dbfs():
    configuration = config.parse('config.toml')
    db = database.get_instance(configuration)
    fs = filesystem.get_instance(configuration)
    return (db, fs)
