import toml

def parse(file):
    result = {}

    data = toml.loads(file)

    result['echo'] = data['echo']['value']

    return result
