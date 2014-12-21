"""
usage: mdms modify <uuid> name <name>
       mdms modify <uuid> date <date>
       mdms modify <uuid> extra <extra>
       mdms modify <uuid> add tag <tag>
       mdms modify <uuid> remove tag <tag>
       mdms modify <uuid> add file <file>
       mdms modify <uuid> remove file <file>
"""

from docopt import docopt
import uuid as uuidlib
import dateutil.parser

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

    if args['name'] is True:
        doc.name = args['<name>']
    elif args['date'] is True:
        try:
            date = dateutil.parser.parse(args['<date>'])
        except ValueError:
            print("Invalid date")
        doc.document_date = date
    elif args['extra'] is True:
        doc.extra = args['<extra>']
    elif args['tag'] is True:
        tag = args['<tag>']
        if args['add'] is True:
            doc.add_tag(tag)
        else:
            doc.remove_tag(tag)
    elif args['file'] is True:
        filename = args['<file>']
        if args['add'] is True:
            fs.add(doc.uuid, filename)
        else:
            fs.remove(doc.uuid, filename)
    db.save(doc)
