In order to quickly install all required packages in your python venv run the following command on it:

(venv) $ pip install -r requirements.txt

This will recreate a perfect replica of venv used for development

THIS IS A TEST FOR COMMITS

REQUIREMENT VERSION LOG
filename : requirement.txt
Last update date : 20/03/09

 ---- COMMIT LOG FROM PREVIOUS GITHUB FOLDER ------
Tot n of commits : 18

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
