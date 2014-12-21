"""
usage: mdms remove <uuid> [--force]

options:
    --force, -f     Remove without asking
"""

from docopt import docopt
import uuid as uuidlib
import util

def main(argv, db, fs):
    args = docopt(__doc__, argv = argv)

    try:
        uuid = uuidlib.UUID(args['<uuid>'])
    except ValueError:
        print("Invalid uuid")
        return

    doc = db.load(uuid)
    if doc is None:
        print("Document not found")
        return

    if args['--force'] is not True:
        sure = util.query_yes_no("Are you sure?", default="no")
        if sure == False:
            return

    fs.remove_dir(uuid)
    db.remove(doc)
