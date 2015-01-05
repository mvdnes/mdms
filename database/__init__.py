def get_instance(configuration):
    if "database" not in configuration:
        raise KeyError("Did not found database in configuration")
    if "type" not in configuration['database']:
        raise KeyError("Could not determine database type to use")

    dbtype = configuration['database']['type']
    if dbtype == 'sqlite':
        return sqlite.MdmsSqlite(configuration['database'])
    else:
        raise ValueError("Invalid database type")

def virtual(_):
    def raiser(_):
        raise NotImplementedError

    return raiser

class MdmsDatabase:
    @virtual
    def save(self, document):
        pass

    @virtual
    def load(self, uuid=None, raw_uuid=None):
        pass

    @virtual
    def search(self, tags, from_date, to_date):
        pass

    @virtual
    def tagcount(self):
        pass

    @virtual
    def tagless(self):
        pass

    @virtual
    def remove(self):
        pass

class ExistsError(Exception):
    pass

from . import sqlite
