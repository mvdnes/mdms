import uuid as uuidlib
import datetime

class Document:
    def __init__(self,
            uuid=None, name="",
            creation_date=None,
            document_date=None,
            tags=set(),
            extra="",
            in_database=False):
        if uuid is None:
            self.uuid = uuidlib.uuid4()
        else:
            self.uuid = uuid
        self.name = name
        if creation_date is None:
            self.creation_date = datetime.datetime.now()
        else:
            self.creation_date = creation_date
        if document_date is None:
            self.document_date = datetime.datetime.now()
        else:
            self.document_date = document_date
        self.tags = tags
        self.extra = extra
        self.in_database = in_database

    def add_tag(self, tag):
        self.tags.add(tag)

    def remove_tag(self, tag):
        self.tags.remove(tag)
