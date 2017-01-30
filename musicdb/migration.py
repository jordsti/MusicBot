import hashlib
import os
import imp
import inspect
import time

def generate_structures_hash(connection):
    cur = connection.cursor()
    tables = []
    query = """SHOW TABLES"""
    cur.execute(query)
    rows = cur.fetchall()

    for row in rows:
        tables.append(row[0])

    sha256 = hashlib.sha256()
    structure_string = ""
    query = """DESCRIBE {0};"""
    for table in tables:
        cur.execute(query.format(table))
        rows = cur.fetchall()
        structure_string += "TableName={0}\n".format(table)
        for row in rows:
            structure_string += "Column={0},{1},{2},{3},{4},{5}\n".format(row[0], row[1], row[2], row[3], row[4], row[5])

    sha256.update(structure_string.encode('ascii'))
    cur.close()
    return sha256.hexdigest()


class DbStructureVersion:
    def __init__(self, migration_name, structure_hash, executed_on, version_number, id=0):
        self.migration_name = migration_name
        self.structure_hash = structure_hash
        self.executed_on = executed_on
        self.version_number = version_number
        self.id = id


class MigrationInformationParser:
    def __init__(self):
        self.informations = {}

    def read_file(self, file_path):
        fp = open(file_path, 'r')
        lines = fp.readlines()

        for l in lines:
            line = l.rstrip('\n').rstrip('\r').rstrip()
            if not line.startswith('#'):
                try:
                    data = line.split('=')
                    var_name = data[0].rstrip().lstrip()
                    var_data = data[1].rstrip().lstrip()
                    self.informations[var_name] = var_data

                except Exception as e:
                    print("Error in migration information file: {0}".format(e))

        fp.close()


class Migration:
    def __init__(self, migration_name, version_number):
        self.migration_name = migration_name
        self.version_number = version_number
        self.metadata = {}
        self.parent_dir = ""
        self.file_path = ""
        self.__load_metadata()

    def __load_metadata(self):
        file_path = inspect.getfile(self.__class__)
        parent_dir = os.path.dirname(file_path)
        self.file_path = file_path
        self.parent_dir = parent_dir

        information_parser = MigrationInformationParser()
        information_parser.read_file(os.path.join(parent_dir, "{0}.meta".format(self.__class__.__name__)))
        self.metadata["hash"] = information_parser.informations["hash"]

    def hash(self):
        return self.metadata["hash"]

    def up(self, connection):
        pass

    def down(self, connection):
        pass


class MigrationManager:
    def __init__(self, database):
        self.migrations_folder = "musicdb/migrations/"
        self.migrations = []
        self.database = database
        self.__load_migrations()

    def __load_migrations(self):
        import musicdb.migrations
        for name, obj in inspect.getmembers(musicdb.migrations):
            if inspect.isclass(obj):
                try:
                    mig = obj()
                    self.migrations.append(mig)
                except Exception as e:
                    print("Error while instantiating the migration: {0}".format(e))

        self.migrations = sorted(self.migrations, key=lambda migration: migration.version_number)

    def new_migration(self, migration_name):
        if not migration_name.endswith('Migration'):
            migration_name = "{0}Migration".format(migration_name)

        for m in self.migrations:
            if m.migration_name == migration_name:
                print("Migration {0} already exists...".format(migration_name))
                return

        migration_template = ""
        file_path = inspect.getfile(self.__class__)
        root_path = os.path.dirname(file_path)
        fp = open(os.path.join(root_path, "migration.tpl"))

        lines = fp.readlines()

        for l in lines:
            migration_template += l

        fp.close()

        version_number = 1

        if len(self.migrations) > 0:
            version_number = self.migrations[-1].version_number + 1

        # generating python stub
        migration_template = migration_template.replace("%MIGRATION_NAME%", migration_name)
        migration_template = migration_template.replace("%MIGRATION_NUMBER%", str(version_number))
        meta_template = "# Meta migration file\nhash=None\n"

        fp = open(os.path.join(root_path, 'migrations', "{0}.py".format(migration_name)), 'w')
        fp.write(migration_template)
        fp.close()

        # generating meta file
        fp = open(os.path.join(root_path, 'migrations', "{0}.meta".format(migration_name)), 'w')
        fp.write(meta_template)
        fp.close()

        # adding __init__ entry
        fp = open(os.path.join(root_path, 'migrations', '__init__.py'), 'a')
        fp.write("# Migration Version {0}, Added On {1}\n".format(version_number, int(time.time())))
        fp.write("from .{0} import {0}\n".format(migration_name))
        fp.close()

        print("Migration {0} added with version number {1}".format(migration_name, version_number))
        print("Run update-migration command to update migration hash to current structure, this will run your last migration and update your current schema".format(migration_name))

    def update_migration(self):
        if len(self.migrations) == 0:
            print("No migration found !")
            return

        migration = self.migrations[-1]
        if not migration.hash() == 'None':
            print("Migration was already updated")
            return

        # verifying if we currently match the hash
        versions = self.database.get_db_versions()
        if len(versions) == 0:
            print("No database schema version found !, you must initialize your database first")
            return

        last_version = versions[-1]

        conn = self.database.connect()
        db_hash = generate_structures_hash(conn)

        if not last_version.structure_hash == db_hash:
            print("Your database doesn't match current schema, fix your schema first")

        print("Running {0}...".format(migration.migration_name))
        rs = False
        try:
            migration.up(conn)
            rs = True
        except Exception as e:
            print("Exception in Migration: {0}".format(e))

        if rs:
            print("Migration executed with success")
            # updating meta hash
            meta_file = os.path.join(migration.parent_dir, "{0}.meta".format(migration.migration_name))
            # adding version in database
            db_hash = generate_structures_hash(conn)

            fp = open(meta_file, 'w')
            fp.write("# Meta migration file\nhash={0}\n".format(db_hash))

            db_version = DbStructureVersion(migration.migration_name, db_hash, int(time.time()), migration.version_number)
            conn.close()
            self.database.add_db_version(db_version)
        else:
            print("Error in migration..")

    def get_migration_by_version_number(self, version_number):
        for m in self.migrations:
            if m.version_number == version_number:
                return m

        return None

    def upgrade_to(self, target_version_number):
        versions = self.database.get_db_versions()
        if len(versions) == 0:
            print("No version found in database schema")
            return

        target_version = None
        m = self.get_migration_by_version_number(target_version_number)
        if m:
            target_version = m

        if target_version is None:
            print("Target version not found")
            return

        current_version = versions[-1]

        if target_version.version_number <= current_version.version_number:
            print("Schema is already more recent or at the same version as target version")
            return

        # verifying if we currently matching
        conn = self.database.connect()
        db_hash = generate_structures_hash(conn)

        if not db_hash == current_version.structure_hash:
            print("Schema hash not matching current version")
            return

        while current_version.version_number != target_version.version_number:
            new_version = current_version.version_number + 1
            migration = self.get_migration_by_version_number(new_version)

            if migration is None:
                print("Migration Version #{0} not found".format(new_version))
                break

            try:
                migration.up(conn)

                db_hash = generate_structures_hash(conn)
                if not db_hash == migration.hash():
                    print("Schema hash not matching version #{0}".format(migration.version_number))
                    break

                # adding version
                current_version = DbStructureVersion(migration.migration_name, db_hash, int(time.time()), migration.version_number)
                self.database.add_db_version(current_version)
                print("Schema updated to version #{0}".format(migration.version_number))

            except Exception as e:
                print("Error during running {0}".format(migration.migration_name))
                break

        conn.close()

    def revert_to(self, target_version_number):
        versions = self.database.get_db_versions()
        if len(versions) == 0:
            print("No version found in database schema")
            return

        target_version = None

        for v in versions:
            if v.version_number == target_version_number:
                target_version = v
                break

        if target_version is None:
            print("Target version not found")
            return

        current_version = versions[-1]

        conn = self.database.connect()

        while current_version.version_number != target_version.version_number:
            if current_version.version_number == 0:
                # nothing to do here
                break

            migration = self.get_migration_by_version_number(current_version.version_number)
            if migration is None:
                print("Missing migration number #{0}".format(current_version.version_number))
                break

            db_hash = generate_structures_hash(conn)

            if not db_hash == migration.hash():
                print("Schema hash not matching!, Migration #{0}".format(current_version.version_number))
                break

            try:
                migration.down(conn)
            except Exception as e:
                print("Migration version #{0} fail: {1}".format(migration.version_number, e))
                break

            index = versions.index(current_version)
            self.database.remove_db_version(current_version)
            current_version = versions[index-1]

            print("Schema reverted to version #{0}".format(current_version.version_number))

        conn.close()

    def run_migrations(self):
        versions = self.database.get_db_versions()
        current_version = versions[-1]

        if len(self.migrations) == 0:
            print("Database Schema is up-to-date")
            return

        last_migration = self.migrations[-1]

        if current_version.version_number == last_migration.version_number:
            print("Database Schema is up-to-date")
        else:
            print("Upgrading Database Schema to version #{0}".format(last_migration.version_number))
            self.upgrade_to(last_migration.version_number)
