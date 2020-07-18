== REQUIREMENT VERSION LOG ====================|
filename : requirements/req-common.txt
Last update date : 20/13/10 (yy/mm/dd)
************************************************|

== INSTALLATION ON NEW MACHINES =======================================================================================|

WARNING: THIS PROJECT HAS BEEN DEVELOPED WITH VERSION 3.8 OF PYTHON. (Download it here: https://www.python.org/downloads/)

To recreate an exact working replica of python3.x venv used during development, follow the instruction below.

If you currently have installed on your machines multiple version of the interpreter, please select v.3 to create the
virtual environment. To do this, run this command in your terminal:

		(1)  $ python3 -m venv venv

otherwise, if python3 is the only version you use of the interpreter, run the following command instead:

	   (1*)  $ python -m venv venv

The former commands will create a folder called 'venv' inside your current working directory. 'venv' will host all
TeamPicks dependencies without messing up with (or damaging) your machine global python interpreter.

You can now run the following commands to complete the procedure and automatically install all needed dependencies:

		Windows machines:
		(2)    $ venv\Scripts\activate

		Macintosh machines:
		(2*)   $ source venv/bin/activate

		then:
		(3)    (venv) $ pip install -r requirements/req-common.txt
		(4)    (venv) $ pip install -r requirements/req-dev.txt
		(5)     set-up a .env file (read how in the section below)

You are ready to go! (we hope)

Some additional information:

(!) If any package raise you any exception please downgrade requirements to stable-only package version by using the
following commands in your terminal :

	    $ venv\Scripts\activate
	    (venv) $ pip uninstall -r requirements/req-common.txt
	    (venv) $ pip uninstall -r requirements/req-dev.txt
	    (venv) $ pip install -r requirements/req-common-stable.txt
	    (venv) $ pip install -r requirements/req-dev-stable.txt

(!) To update all existing used packages to their latest versions, please run the following commands in your terminal:

	    $ venv\Scripts\activate
	    (venv) pip install --upgrade -r requirements/req-common.txt
	    (venv) pip install --upgrade -r requirements/req-dev.txt

(!) To create or update a package-log file named 'requirements.txt' of all currently used modules by app, run the
following command in your terminal :

	    (venv) $ pip freeze >requirements/req-common-stable.txt

(!) To factory reset your (venv) to only original python distribution libraries of your main python interpreter, run the
following commands in your terminal :

	    (venv) $ pip uninstall -r requirements/req-common.txt
	    (venv) $ pip uninstall -r requirements/req-dev.txt

(!) To turn your (venv) off :

	    $ venv\Scripts\deactivate

***********************************************************************************************************************|


== THE DOT-ENV FILE ========================================================================================================|

If you have a look at "config.py" file you will notice that config attributes are passed to the app object in an apparently
self-referential way. Where are the real config values? To answer this question we introduce you to the ".env" file. Nothing
"we" created but something very useful to host app-config constants in the system environment. This prevents you to:

1) manually type them in the terminal every time you set-up a new machine to work with TeamPicks
2) to expose sensitive data into hard-coded values (e.g. Email provider credentials, SECRET_KEY value - remembering you
	that this latter one is used to encrypt post requests in your flask app) when sharing config files or, in general, to
	expose them in the first place.

You can set-up a .env file yourself simply creating a new text files where you specify which key is equal to what.

		<CONFIG_KEY>=<config_key value>

Use the following as an example :

{{ example-file: .env }}----------------------------
SECRET_KEY=very_difficult_cats_to_find
SQLALCHEMY_DATABASE_URI=<relative URI of db>
MAIL_SERVER =smtp.googlemail.com
MAIL_USERNAME=<email_provider_login_credentials>
MAIL_PASSWORD=no_one_will_guess_that
FLASKY_ADMIN=app_admin@email.com
FLASK_ENV=development
USERS_UPLOADS_BIN=\static\users
PUBS_UPLOADS_BIN=\static\pubs

{{ end_file}}---------------------------------------

The ".flaskenv" is another example of a valid .env file structure.
***********************************************************************************************************************|


== DUMMY POPULATE DATABASES ===========================================================================================|

The TeamPicks project comes bundled with a very handy developers' toolkit : check it out in the "devkit.py" file.

Here you find the create_userbase() func. This is an engine to quickly (and automatically) populate a brand new local
database (e.g. sqlite). Of course this step is crucial in order to let the developer (you) to fully understand how TeamPicks work
right now and what still has to be done. create_userbase() directly invoke the dummy() func. This latter one is exactly
where new user/owner/pub/groups and so on gets created. Even if more advanced configurations can be used, the basic
use-case for create_userbase() func is as follow:

		(venv) $ flask shell    ( tests will run ... continue if you do not get any error )
		(venv) $ from devkit import create_userbase
		(venv) $ create_userbase(items=int("int_of_target_user_population"))

If you are even lazier, the new straightfoward "populate" CLI (command-line-interface) flask command has been added to the
app object. This will populate for you all your existing databases (after all connection tests have passed) with a number of
new dummy items, set by default to 50 units. of course, this latter one can be overwritten accordingly to tastes and needs.
Using "populate" is really straight-forward:

		  (1) $ flask shell
		  (2) $ flask populate <items>

Done! Now start the flask server and browse the app taking the role of one of this puppies by logging in with the following
credentials:

		username ->     < choose_one_from_db >
		password ->     "password"

Of course nothing prevents you to create your own account on the platform.
***********************************************************************************************************************|


== CLI COMMANDS =======================================================================================================|
To quickly create new db files capable of plugging-in correctly with all config profiles, the following click commands are
available :

	    (venv) $ flask reset [config_key]
	    (venv) $ flask build [config_key]

If not specified, commands will print a menu where to choose which config profile to load.
Use 'env' argument in order to let < reset > and < build > commands look in sys environment variables for config profile to
load.
************************************************************************************************************************|


=== COMMITS LOG FROM PREVIOUS GITHUB FOLDER ===========================================================================|
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

************************************************************************************************************************|