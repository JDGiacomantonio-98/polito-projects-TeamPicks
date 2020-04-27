# DATABASE OBJECT CLASS SPECIFICATION MODULE
# SQLAlchemy produces Object-Oriented Databases
from flask import session, current_app
from app import db, login_handler
from itsdangerous import TimedJSONWebSignatureSerializer as timedTokenizer
from flask_login import UserMixin

# DATABASE GLOBAL FUNCTIONS #


@login_handler.user_loader
def loadUser(user_id):

    if session.get('dbModelType') == 'user':
        return User.query.get(user_id)
    else:
        return Owner.query.get(user_id)

# DATABASE OBJECTS STRUCTURE #


class USER(db.Model, UserMixin):
    # {} named userInfo would better suit the role of specific user infos container
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False, index=True)
    email = db.Column(db.String, unique=True, nullable=False, index=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    lastSession = db.Column(db.DateTime, nullable=True)     # nullable=True temporary solution until dates management
    firstName = db.Column(db.String(60), unique=False, nullable=False)
    lastName = db.Column(db.String(60), unique=False, nullable=False)
    age = db.Column(db.Integer, unique=False, nullable=True)
    sex = db.Column(db.String)
    img = db.Column(db.String)     # stores the filename string of the img file
    about_me = db.Column(db.Text)
    city = db.Column(db.String, nullable=True)

    pswHash = db.Column(db.String(60), unique=False, nullable=False)    # stores hashed user password

    def fingerPrint(self):
        print('USER :\n')
        for attr, value in self.__dict__.items():
            print("{} : {}\n".format(attr, value))

    def createToken(self, expireInSec=(8*60)):
        return timedTokenizer(current_app.config['SECRET_KEY'], expireInSec).dumps({'user-id': self.id}).decode('utf-8')

    @staticmethod
    def confirmAccount(token):
        try:
            user_id = timedTokenizer(current_app.config['SECRET_KEY']).loads(token)['user-id']
            user = User.query.get(user_id)
        except:
            return None
        if user_id != user.id:
            user.confirmed = False
            db.session.commit()
            return None
        else:
            user.confirmed = True
            db.session.commit()
            return user

    @staticmethod
    def verifyToken_pswReset(resetToken):
        try:
            userID = timedTokenizer(current_app.config['SECRET_KEY']).loads(resetToken)['user-id']
        except:
            return None
        return User.query.get(userID)


class User(USER):
    __tablename__ = 'users'

    sports = db.Column(db.Boolean)    # relationship
    groups = db.Column(db.Boolean)    # relationship


class Owner(USER):
    __tablename__ = 'owners'

    pub = db.Column(db.Boolean)  # creates one-to-one relationship between owner and his pub
    subsType = db.Column(db.String, nullable=False, default='free-acc') # stores hex codes whose refers to different acc-subscriptions
    subsExpirationDate = db.Column(db.DateTime, nullable=True)       # should be not nullable


class Pub(db.Model):
    __tablename__ = 'pubs'

    id = db.Column(db.Integer, primary_key=True)
    ownerCredentials = db.Column(db.Boolean)      # backref to owner firstname + lastname
    #ownerLastName = db.Column(db.String, nullable=False)
    businessAddress = db.Column(db.String, nullable=False)
    isBookable = db.Column(db.Boolean, nullable=False)
    seatsMax = db.Column(db.Integer, nullable=False)
    seatsBooked = db.Column(db.Integer, nullable=False, default=0)
    rating = db.Column(db.Integer, nullable=False, default=0)
    businessDescription = db.Column(db.Text, nullable=True, default='let your customer know what you do best.')


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True, nullable=False)
    administrator = db.Column(db.String(15), unique=True, nullable=False)
    members = db.Column(db.Integer, default=0)
    watchlist = db.Column(db.String, default="")    # stores list of matches the group want to see this week


class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Binary, nullable=False)
    date = db.Column(db.DateTime)
    opponents = db.Column(db.String, nullable=False)    # stores the two teams who will play against each other


