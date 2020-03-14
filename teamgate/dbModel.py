# DATABASE OBJECT CLASS SPECIFICATION MODULE
# SQLAlchemy produces Object-Oriented Databases

from teamgate import app, db, loginManager
from itsdangerous import TimedJSONWebSignatureSerializer as timedTokenizer
from flask_login import UserMixin

# DATABASE LEVEL FUNCTIONS #


@loginManager.user_loader
def loadUser(userID):
    return User.query.get(userID)

# DATABASE OBJECT STRUCTURE #


class USER(db.Model, UserMixin):
    """A {} named userInfo would better suit the role of specific user infos container """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    city = db.Column(db.String, nullable=True)
    email = db.Column(db.String, unique=True, nullable=False)

    """ nullable=True is only a temporary solution """
    lastSession = db.Column(db.DateTime, nullable=True)

    """ Following value stores hashed user password """
    pswHash = db.Column(db.String(60), unique=False, nullable=False)
    type = db.Column(db.String)

    def create_ResetToken(self, expireInSec=900):
        return timedTokenizer(app.config['SECRET_KEY'], expireInSec).dumps({'userID': self.id}).decode('utf-8')

    @staticmethod
    def verify_ResetToken(resetToken):
        try:
            userID = timedTokenizer(app.config['SECRET_KEY']).loads(resetToken)['userID']
        except:
            return None
        return User.query.get(userID)

    def __str__(self):
        return "USER n.{}\ntype=\t'user'\nusername=\t{}\nemail address=\t{}\nfirst Name=\t{}\nLast Name=\t{}\nLast time online=\t{}".format(self.id, self.username, self.email, self.firstName, self.lastName, self.lastSession)


class User(USER):
    __tablename__ = 'users'

    firstName = db.Column(db.String(), unique=False, nullable=False)
    lastName = db.Column(db.String(120), unique=False, nullable=False)
    age = db.Column(db.Integer, unique=False, nullable=True)
    sex = db.Column(db.String)
    img = db.Column(db.String)
    """Following columns should store list object"""
    sports = db.Column(db.Integer, nullable=True)
    groups = db.Column(db.Integer, nullable=True)


class Pub(USER):
    __tablename__ = 'pubs'

    ownerFirstName = db.Column(db.String, nullable=False)
    ownerLastName = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    bookable = db.Column(db.Boolean, nullable=False)
    seatsMax = db.Column(db.Integer, nullable=False)
    seatsBooked = db.Column(db.Integer, nullable=False)
    subsType = db.Column(db.Binary, nullable=False)
    subsExpirationDate = db.Column(db.DateTime, nullable=False)


class Group(db.Model):
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


