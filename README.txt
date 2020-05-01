To recreate an exact working replica of python3.x venv used during development, run the following commands in your terminal :

    $ python -m venv venv
    $ venv\Scripts\activate

    (venv) $ pip install -r requirements/req-common.txt
    (venv) $ pip install -r requirements/req-dev.txt

If any package raise any exception please downgrade requirements to stable-only package version by using the following commands in your terminal :

    (venv) $ pip install -r requirements/req-common-stable.txt
    (venv) $ pip install -r requirements/req-dev-stable.txt

To switch venv off :

        $ venv\Scripts\deactivate

To quickly create or update a package-log file named 'requirements.txt' of all currently used modules by app, run the following command in your terminal :

    (venv) $ pip freeze >requirements/req-common.txt

To fully reset  your venv to only original python libraries in your main python interpreter, run the following commands in your terminal :

    (venv) $ pip uninstall -r requirements/req-common.txt
    (venv) $ pip uninstall -r requirements/req-dev.txt

To quickly create new db files capable of plugging-in correctly with all config profiles, the following click commands are available :

    (venv) $ flask reset [config_key]
    (venv) $ flask build [config_key]

If not specificied, commands will print a menu where to choose which config profile to load.
Use 'env' argument in order to let < reset > and < build > commands look in sys environment variables for config profile to load.

++++++++++++++++++++++++++++++++++++++++++++++++++++|
REQUIREMENT VERSION LOG
filename : requirements.txt
Last update date : 20/04/16
++++++++++++++++++++++++++++++++++++++++++++++++++++|

 ---- COMMIT LOG FROM PREVIOUS GITHUB FOLDER ------
Tot n of commits before moving : 18

v0.2.4.2
    - profile update function has been refinished and now efficiently support profile image updating

v0.2.4.1
    - User profile update function implemented

v0.2.3.1
    - Class inheritance in dbModel has been implemented throght __abstract__ = True parameter of SQLAlchemy
    - Other minor adjustments in registration/login routes functioning and templating

v0.2.3
    - Registration form is able to send data to user Database
    - User database accept basic queries

v0.2.2.2
    - Fixed an issue whose caused a error banner to be displayed even if no data had been insert into login form

v0.2.2.1
    - Fixed an issue whose cause an error banner to be displayed even if no data had been insert into registration form

v0.2.2
    - Registration and Login forms now use method=POST in order to store and compare user inputted data
    - Redirecting path after registration now works properly

v0.2.1
    - Fixed a bug whose let the form basic validation to not work properly
    - Fixed a bug whose let Pycharm not recognise templates folder

v0.2
    - TeamGATE app is now structured as a python package
