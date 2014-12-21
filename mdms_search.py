"""
usage: mdms search --uuid=<uuid>
       mdms search [--from=<from>] [--to=<to>] (<tags>...)

options:
    --from=<from>   starting date to search from
    --to=<to>       end date to search to
"""

from docopt import docopt
import uuid as uuidlib
import dateutil.parser
import datetime

def main(argv, db, fs):
    args = docopt(__doc__, argv = argv)
    if args['--uuid'] is not None:
        find_uuid(args['--uuid'], db, fs)
    else:
        find_tags(args['<tags>'], args['--from'], args['--to'], db, fs)

def print_document(doc, filelist):
    files = "\n".join(filelist)
    tags = ", ".join(doc.tags)
    
    print("""UUID:           {0}
Document name:  {1}
Document date:  {2}
Created date:   {3}
Tags:           {4}
Extra info:     {5}
Files:
{6}
""".format(
            doc.uuid,
            doc.name,
            doc.document_date,
            doc.creation_date,
            tags,
            doc.extra,
            files))

def find_uuid(uuid_string, db, fs):
    try:
        uuid = uuidlib.UUID(uuid_string)
    except:
        print("Invalid uuid specified")
        return

    doc = db.load(uuid)
    if doc is None:
        print("Could not find document")
    files = fs.get(uuid)
    print_document(doc, files)

def find_tags(tags, from_raw, to_raw, db, fs):
    try:
        if from_raw is None:
            from_date = datetime.datetime.min
        else:
            from_date = dateutil.parser.parse(from_raw)
        if to_raw is None:
            to_date = datetime.datetime.max
        else:
            to_date = dateutil.parser.parse(to_raw)
    except ValueError:
        print("Invalid to or from date")
        return

    docs = db.search(tags, from_date, to_date)
    if len(docs) == 0:
        print("No documents found")
    for doc in docs:
        files = fs.get(doc.uuid)
        print_document(doc, files)
