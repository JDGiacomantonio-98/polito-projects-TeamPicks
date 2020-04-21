# DATABASE OBJECT CLASS SPECIFICATION MODULE
# SQLAlchemy produces Object-Oriented Databases
from flask import session, current_app
from app import db, login_handler
from itsdangerous import TimedJSONWebSignatureSerializer as timedTokenizer
from flask_login import UserMixin

# DATABASE LEVEL FUNCTIONS #

# this function has to be adapted to our purposes because we have not an only db.Model type but two
# I m think of overriding some flask-login source functions


@login_handler.user_loader
def loadUser(user_id):

    if session.get('dbModelType') == 'user':
        return User.query.get(user_id)
    else:
        return Pub.query.get(user_id)

# DATABASE OBJECT STRUCTURE #


class USER(db.Model, UserMixin):
    # {} named userInfo would better suit the role of specific user infos container
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    # for Pubs username will be identify their businessName
    username = db.Column(db.String(15), unique=True, nullable=False)
    city = db.Column(db.String, nullable=True)
    email = db.Column(db.String, unique=True, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    # Following value stores hashed user password
    pswHash = db.Column(db.String(60), unique=False, nullable=False)

    def createToken(self, expireInSec=(8*60)):
        return timedTokenizer(current_app.config['SECRET_KEY'], expireInSec).dumps({'user-id': self.id}).decode('utf-8')

    @staticmethod
    def confirmAccount(token):
        try:
            userID = timedTokenizer(current_app.config['SECRET_KEY']).loads(token)['user-id']
            user = User.query.get(userID)
        except:
            return None
        if userID != user.id:
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

    firstName = db.Column(db.String(), unique=False, nullable=False)
    lastName = db.Column(db.String(120), unique=False, nullable=False)
    age = db.Column(db.Integer, unique=False, nullable=True)
    sex = db.Column(db.String)
    img = db.Column(db.String)
    about_me = db.Column(db.Text)
    """Following columns should store list object"""
    sports = db.Column(db.Integer, nullable=True)
    groups = db.Column(db.Integer, nullable=True)

    """ nullable=True is only a temporary solution """
    lastSession = db.Column(db.DateTime, nullable=True)

    def fingerPrint(self):
        for attr, value in self.__dict__.items():
            print(attr, value)


class Pub(USER):
    __tablename__ = 'local-partners'

    ownerFirstName = db.Column(db.String, nullable=False)
    ownerLastName = db.Column(db.String, nullable=False)
    businessAddress = db.Column(db.String, nullable=False)
    isBookable = db.Column(db.Boolean, nullable=False)
    seatsMax = db.Column(db.Integer, nullable=False)
    seatsBooked = db.Column(db.Integer, nullable=False, default=0)
    businessRating = db.Column(db.Integer, nullable=False, default=0)
    # in future the following column should store only hex codes to name different acc-subscriptions
    subsType = db.Column(db.String, nullable=False, default='free-acc')
    # following value should be not nullable
    subsExpirationDate = db.Column(db.DateTime, nullable=True)
    businessDescription = db.Column(db.Text, nullable=True, default='let your customer know what you do best.')


class Group(db.Model):
    __tablename__='groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True, nullable=False)
    administrator = db.Column(db.String(15), unique=True, nullable=False)
    members = db.Column(db.Integer, default=0)
    """ The following parameter store the list of matches the group want to see this week """
    watchlist = db.Column(db.String, default="")


class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Binary, nullable=False)
    date = db.Column(db.DateTime)
    """ The following parameter stores the two teams who will play against each other """
    opponents = db.Column(db.String, nullable=False)


