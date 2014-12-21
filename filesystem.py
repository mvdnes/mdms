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

    def get(self, uuid):
        result = []
        directory = self.get_dir(uuid)
        for (dirpath, dirnames, filenames) in os.walk(directory):
            result = filenames
            break # We only want the top level dir
        return [directory + r for r in result]

    def remove(self, uuid, file):
        full = self.get_dir(uuid) + file
        os.remove(full)
