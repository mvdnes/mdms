"""
usage: mdms create [--date=<date>] [--extra=<extra>] --name=<name> (--tag=<tag>...) (--file=<file>...)

options:
    --name=<name>       Name of the document
    --date=<date>       Date of the document
    --extra=<extra>     Extra information
    --tag=<tag>, -t     Tag(s) to add
    --file=<file>, -f   File(s) to copy
"""

from docopt import docopt
import dateutil.parser
import document

def main(argv, db, fs):
    args = docopt(__doc__, argv = argv)

    name = args['--name']
    if args['--date'] is None:
        date = None
    else:
        try:
            date = dateutil.parser.parse(args['--date'])
        except ValueError:
            print("Invalid date specified")
            return
    extra = args['--extra']
    tags = set(args['--tag'])

    doc = document.Document(name = name,
            document_date = date,
            extra = extra,
            tags = tags)
    db.save(doc)

    for f in args['--file']:
        fs.add(doc.uuid, f)

    print(str(doc.uuid))
