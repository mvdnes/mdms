import pytoml

def parse(file):
    with open(file) as conffile:
        data = pytoml.loads(conffile.read())

    return data
