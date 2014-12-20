import toml

def parse(file):
    with open(file) as conffile:
        data = toml.loads(conffile.read())

    return data
