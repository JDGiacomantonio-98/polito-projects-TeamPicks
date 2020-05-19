def create_userbase(items=None, test_db=False):
    from app.dbModels import dummy
    if test_db:
        items = 1
    elif items is None:
        items = (input('Please select how many object will the userbase be composed of :\t'))
        while not items.isnumeric():
            print('Input error: only a numeric value can be submitted. Try again.')
            items = (input('Please select how many object will the userbase be composed of :\t'))
    elif type(items) != int:
        while not items.isnumeric():
            print('Input error: only a numeric value can be submitted. Try again.')
            items = (input('Please select how many object will the userbase be composed of :\t'))
        items = int(items)
    userbase = {
        'user': 'u',
        'owner': 'o'
    }
    for k in userbase:
        if test_db:
            dummy(single=False, model=userbase[k], items=items, feedback=False)
        else:
            dummy(single=False, model=userbase[k], items=items)


def config_menu():
    # print a menu to create different instances of app working with different Configs profiles
    choices = ['', 'd', 't', 'p', 'q']
    print('==================')
    k = str(input('SELECT APP ENV (on this machine)\n'
                  '==================\n'
                  '[D]evelopment\n'
                  '[T]esting\n'
                  '[P]roduction\n\n'
                  '[Q]uit process\n'
                  'press < Enter > to run Defaults :\t'
                  )
            ).lower()
    while k.isnumeric() or (k not in choices):
        print('Invalid input : please choose from menu options.')
        k = str(input('SELECT APP ENV (on this machine)\n'
                      '==================\n'
                      '[D]evelopment\n'
                      '[T]esting\n'
                      '[P]roduction\n\n'
                      '[Q]uit process\n'
                      'press < Enter > to run Defaults :\t'
                      )
                ).lower()
    if k == 'q':
        quit()
    if k == '':
        k = 'd'
    return k


def set_env(selKey):
    from os import path, getenv
    from dotenv import load_dotenv

    envs = {
        'd': 'development',
        't': 'testing',
        'p': 'production',
    }

    basedir = path.abspath(path.dirname(__file__))
    load_dotenv(path.join(basedir, '.env'))
    e = getenv('FLASK_ENV')
    if e is None:
        with open(path.join(basedir, '.env'), 'a') as f:
            f.write(f'\nFLASK_ENV={envs[selKey]}')
            return envs[selKey]
    elif e != envs[selKey]:
        with open(path.join(basedir, '.env'), 'r') as f:
            lines = f.readlines()
        with open(path.join(basedir, '.env'), 'w') as f:
            for line in lines:
                if 'FLASK_ENV=' in line:
                    f.write(f'FLASK_ENV={envs[selKey]}')
                else:
                    f.write(line)
    return envs[selKey]
