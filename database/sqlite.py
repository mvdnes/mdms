import sqlite3
import document
import datetime
import uuid as uuidlib
import database

class MdmsSqlite(database.MdmsDatabase):
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
        sqlite_uuid = sqlite3.Binary(document.uuid.bytes)
        values = {
            "uuid": sqlite_uuid,
            "name": document.name,
            "document_date": document.document_date.isoformat(),
            "creation_date": document.creation_date.isoformat(),
            "extra": document.extra
        }

        try:
            cursor.execute(stmt, values)
        except sqlite3.IntegrityError:
            raise database.ExistsError()

        cursor.execute("DELETE FROM tag WHERE uuid=:uuid", {"uuid": sqlite_uuid})
        def tag_gen():
            for t in document.tags:
                yield (sqlite_uuid, t)
        cursor.executemany("INSERT INTO tag VALUES (:uuid, :tag)", tag_gen())
        self.conn.commit()

    def load(self, uuid=None, raw_uuid=None):
        cursor = self.conn.cursor()
        stmt = "SELECT name, creation_date, document_date, extra FROM document WHERE uuid = :uuid"
        if raw_uuid is not None:
            uuid = uuidlib.UUID(bytes = raw_uuid)
        sqlite_uuid = sqlite3.Binary(uuid.bytes)
        cursor.execute(stmt, {"uuid": sqlite_uuid})
        result = cursor.fetchone()
        if result is None:
            return None

        stmt = "SELECT tag FROM tag WHERE uuid=:uuid"
        cursor.execute(stmt, {"uuid": sqlite_uuid})
        tags = set([t[0] for t in cursor.fetchall()])

        return document.Document(
            uuid = uuid,
            name = result[0],
            creation_date = datetime.datetime.strptime(result[1], "%Y-%m-%d").date(),
            document_date = datetime.datetime.strptime(result[2], "%Y-%m-%d").date(),
            extra = result[3],
            tags = tags,
            in_database = True,
        )

    def search(self, tags, from_date, to_date):
        cursor = self.conn.cursor()
        stmt = """
SELECT uuid
FROM document
WHERE document_date >= ?
    AND document_date <= ?
"""
        stmt_tag = """
    AND uuid IN (
        SELECT uuid
        FROM tag
        WHERE tag IN (""" + ",".join("?" * len(tags)) + """)
        GROUP BY uuid
        HAVING COUNT(tag) = ?)
"""

        values = [from_date.isoformat(), to_date.isoformat()]
        if len(tags) > 0:
            stmt = stmt + stmt_tag
            values = values + tags + [len(tags)]
        cursor.execute(stmt, values)
        return [self.load(raw_uuid=r[0]) for r in cursor.fetchall()]

    def tagcount(self):
        cursor = self.conn.cursor()
        stmt = "SELECT tag, COUNT(uuid) FROM tag GROUP BY tag"
        cursor.execute(stmt)
        return [{'name': r[0], 'count': r[1]} for r in cursor.fetchall()]

    def tagless(self):
        cursor = self.conn.cursor()
        stmt = "SELECT uuid FROM document WHERE uuid NOT IN (SELECT uuid FROM tag)"
        cursor.execute(stmt)
        return [self.load(raw_uuid=r[0]) for r in cursor.fetchall()]

    def remove(self, doc):
        cursor = self.conn.cursor()
        sqlite_uuid = sqlite3.Binary(doc.uuid.bytes)
        cursor.execute("DELETE FROM document WHERE uuid = ?", (sqlite_uuid,))
        cursor.execute("DELETE FROM tag WHERE uuid = ?", (sqlite_uuid,))
        self.conn.commit()

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
        if old_version < 2:
            cursor.executescript("""
                BEGIN TRANSACTION;
                ALTER TABLE document RENAME TO document_old;
                CREATE TABLE document(uuid BLOB PRIMARY KEY, name TEXT, creation_date TEXT, document_date TEXT, extra TEXT);
                INSERT INTO document(uuid, name, creation_date, document_date, extra) SELECT uuid, name, creation_date, document_date, extra FROM document_old;
                DROP TABLE document_old;
                COMMIT;""")
            self.conn.commit()

            cursor2 = self.conn.cursor()
            cursor.execute("SELECT uuid, creation_date, document_date FROM document");
            while True:
                result = cursor.fetchone()
                if result is None:
                    break
                uuidblob = result[0]
                creation_date = datetime.date.fromtimestamp(int(result[1])).isoformat()
                document_date = datetime.date.fromtimestamp(int(result[2])).isoformat()
                cursor2.execute("UPDATE document SET creation_date = ?, document_date = ? WHERE uuid = ?", (creation_date, document_date, uuidblob))

        cursor.execute("UPDATE config SET value = '2' WHERE key = 'version'")
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
