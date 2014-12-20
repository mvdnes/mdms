import sqlite3
import document
import datetime

class DbSqlite:
    def __init__(self, configuration):
        if "sqlite" not in configuration:
            raise KeyError("database.sqlite not found in configuration")
        sqlite_config = configuration['sqlite']

        if "file" in sqlite_config:
            file = sqlite_config['file']
        else:
            file = "mdms_sqlite.db"

        self.conn = sqlite3.connect(file)
        self.update_db()

    def save(self, document):
        cursor = self.conn.cursor()
        if document.in_database:
            stmt = """UPDATE document SET
                name=:name,
                creation_date=:creation_date,
                document_date=:document_date,
                extra=:extra
                WHERE uuid=:uuid
            """
        else:
            stmt = "INSERT INTO document VALUES (:uuid, :name, :creation_date, :document_date, :extra)"
        values = {
            "uuid": document.uuid.bytes,
            "name": document.name,
            "document_date": int(document.document_date.timestamp()),
            "creation_date": int(document.creation_date.timestamp()),
            "extra": document.extra
        }
        cursor.execute(stmt, values)
        cursor.execute("DELETE FROM tag WHERE uuid=:uuid", {"uuid": document.uuid.bytes})
        def tag_gen():
            for t in document.tags:
                yield (document.uuid.bytes, t)
        cursor.executemany("INSERT INTO tag VALUES (:uuid, :tag)", tag_gen())
        self.conn.commit()

    def load(self, uuid):
        cursor = self.conn.cursor()
        stmt = "SELECT name, creation_date, document_date, extra FROM document WHERE uuid = :uuid"
        cursor.execute(stmt, {"uuid": uuid.bytes})
        result = cursor.fetchone()
        if result is None:
            return None

        stmt = "SELECT tag FROM tag WHERE uuid=:uuid"
        cursor.execute(stmt, {"uuid": uuid.bytes})
        tags = set([t[0] for t in cursor.fetchall()])

        return document.Document(
            uuid = uuid,
            name = result[0],
            creation_date = datetime.datetime.fromtimestamp(result[1]),
            document_date = datetime.datetime.fromtimestamp(result[2]),
            extra = result[3],
            tags = tags,
            in_database = True,
        )

    def update_db(self):
        self.ensure_notempty()
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key='version'")
        result = cursor.fetchone()
        self.update_from_version(int(result[0]))

    def update_from_version(self, old_version):
        cursor = self.conn.cursor()
        if old_version < 1:
            cursor.execute("""
                CREATE TABLE document(
                    uuid BLOB PRIMARY KEY,
                    name TEXT,
                    creation_date INT,
                    document_date INT,
                    extra TEXT)
            """)
            cursor.execute("CREATE TABLE tag(uuid BLOB, tag TEXT, PRIMARY KEY (uuid, tag))")
        cursor.execute("UPDATE config SET value = '1' WHERE key = 'version'")
        self.conn.commit()
    
    def ensure_notempty(self):
        cursor = self.conn.cursor()
        try:
            stmt = "SELECT * FROM config"
            cursor.execute(stmt)
            result = cursor.fetchone()
        except sqlite3.OperationalError:
           stmt = "CREATE TABLE config(key TEXT PRIMARY KEY, value TEXT)"
           cursor.execute(stmt)
           stmt = "INSERT INTO config VALUES ('version', '0')"
           cursor.execute(stmt)
