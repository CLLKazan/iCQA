import datetime

def one_day_from_now():
    return datetime.datetime.now() + datetime.timedelta(days=1)
