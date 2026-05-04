def convert_to_id(name):
    if name not in ['rock', 'paper', 'scissors']:
        raise ValueError('invalid name submitted')
    d = {'rock' : 0, 'paper' : 1, 'scissors' : 2}
    return d[name]

def convert_to_name(id):
    if id not in [0, 1, 2]:
        raise ValueError('invalid id submitted')
    d = {0 : 'rock', 1 : 'paper', 2 : 'scissors'}
    return d[id]
