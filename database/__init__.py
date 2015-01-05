import database.sqlite

def get_instance(configuration):
    if "database" not in configuration:
        raise KeyError("Did not found database in configuration")
    if "type" not in configuration['database']:
        raise KeyError("Could not determine database type to use")

    dbtype = configuration['database']['type']
    if dbtype == 'sqlite':
        return sqlite.DbSqlite(configuration['database'])
    else:
        raise ValueError("Invalid database type")

class ExistsError(Exception):
    pass
