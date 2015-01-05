import datetime

def unixtime(dt):
    epoch = datetime.date.fromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()
