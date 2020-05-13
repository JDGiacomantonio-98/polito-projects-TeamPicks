from app.dbModels import dummy


def create_userbase(items=None):
    if not items:
        items = (input('Please select how many object will the userbase be composed of :\t'))
        while not items.isnumeric():
            print('Input error: only a numeric value can be submitted. Try again.')
            items = (input('Please select how many object will the userbase be composed of :\t'))
        items = int(items)
    userbase = {
        'user': 'u',
        'owner': 'o'
    }
    for k in userbase:
        dummy(single=False, model=userbase[k], items=items)
