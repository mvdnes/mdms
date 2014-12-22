import os
import shutil

def get_instance(configuration):
    return Filesystem(configuration)

class Filesystem:
    def __init__(self, configuration):
        if "filesystem" not in configuration:
            raise KeyError("Filesystem not found in configuration")
        if "location" not in configuration['filesystem']:
            raise KeyError("filesystem.location is not configured")
        self.base = configuration['filesystem']['location']

    def get_dir(self, uuid):
        return self.base + "/" + str(uuid) + "/"

    def add(self, uuid, filepath):
        directory = self.get_dir(uuid)
        if not os.path.exists(directory):
            os.makedirs(directory)
        shutil.copy2(filepath, directory)

    def save(self, uuid, file, filename):
        directory = self.get_dir(uuid)
        if not os.path.exists(directory):
            os.makedirs(directory)
        target = os.path.join(directory, filename)
        file.save(target)

    def get(self, uuid, file=None, basename_only=False):
        result = []
        directory = self.get_dir(uuid)
        for (dirpath, dirnames, filenames) in os.walk(directory):
            result = filenames
            break # We only want the top level dir

        if basename_only:
            prefix = ""
        else:
            prefix = directory

        if file is not None:
            if file in result:
                return prefix + file
            return None

        return [prefix + r for r in result]

    def remove(self, uuid, file):
        full = self.get_dir(uuid) + file
        try:
            os.remove(full)
        except FileNotFoundError:
            return False
        return True

    def remove_dir(self, uuid):
        directory = self.get_dir(uuid)
        try:
            shutil.rmtree(directory)
        except FileNotFoundError:
            pass
