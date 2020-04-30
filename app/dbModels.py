# DATABASE OBJECT CLASS SPECIFICATION MODULE
# SQLAlchemy produces Object-Oriented Databases
from flask import session, current_app
from app import db, login_handler, pswBurner
from itsdangerous import TimedJSONWebSignatureSerializer as timedTokenizer
from flask_login import UserMixin
from faker import Faker
from sqlalchemy.exc import IntegrityError
from math import ceil
from random import randint, random

# DATABASE GLOBAL FUNCTIONS #


@login_handler.user_loader
def loadUser(user_id):

    if session.get('dbModelType') == 'user':
        return User.query.get(user_id)
    else:
        return Owner.query.get(user_id)


def dummy(items=100):
    print('Dummy objects to create : {}\n'.format(items))
    c = str(input('Which type of object do you want to create?\n'
                  '[U]ser\n'
                  '[O]wner\n'
                  '[P]ub\n'
                  '[G]roup\n'
                  '[M]atch\n\n'
                  '[Q]uit\n'
                  'select here : '))
    c = c.lower()
    if c == 'q' or c == '':
        quit()
    else:
        print('Please wait while processing dummy units ...\n')
        rand = Faker()
        flags = [0, 0, 0, 0, 0, 0]
        for i in range(items):
            pswHash = pswBurner.generate_password_hash('password').decode('utf-8')
            if c == 'u' or c == 'users':
                it = User(username=rand.user_name(),
                         email=rand.email(),
                         lastSession=rand.past_date(),
                         firstName=rand.first_name(),
                         lastName=rand.last_name(),
                         age=randint(16, 95),
                         sex=rand.null_boolean(),
                         about_me=rand.text(max_nb_chars=250),
                         city=rand.city(),
                         pswHash=pswHash,
                         )
                it.img = it.set_defaultImg()
                c = 'users'
            elif c == 'o' or c == 'owners':
                it = Owner(username=rand.user_name(),
                         email=rand.email(),
                         lastSession=rand.past_date(),
                         firstName=rand.first_name(),
                         lastName=rand.last_name(),
                         age=randint(18, 95),
                         sex=rand.null_boolean(),
                         about_me=rand.text(max_nb_chars=250),
                         city=rand.city(),
                         pswHash=pswHash,
                         subsType="{0:b}".format(randint(0, 5)),
                         subsExpirationDate=rand.future_date('+90d'),
                         )
                it.img = it.set_defaultImg()
                c = 'owners'
            elif c == 'p' or c == 'pubs':
                print('We are sorry but this function is still under development!')
                quit()
                # it = Pub()
                c = 'pubs'
            elif c == 'g' or c == 'groups':
                print('We are sorry but this function is still under development!')
                quit()
                # it = Group()
                c = 'groups'
            elif c == 'm' or c == 'matches':
                print('We are sorry but this function is still under development!')
                quit()
                # it = Match()
                # c = 'matches'
            db.session.add(it)
            if (i/items) < 0.1 and flags[0] == 0:
                print('*')
                flags[0] = 1
            if (i/items) >= 0.15 and (i/items) < 0.2 and flags[1] == 0:
                print('**')
                flags[1] = 1
            if (i/items) >= 0.2 and (i/items) < 0.4 and flags[2] == 0:
                print('*** 20%')
                flags[2] = 1
            if (i/items) >= 0.4 and (i/items) < 0.6 and flags[3] == 0:
                print('***** 40%')
                flags[3] = 1
            if (i/items) >= 0.6 and (i/items) < 0.8 and flags[4] == 0:
                print('******* 60%')
                flags[4] = 1
            if (i/items) >= 0.8 and (i/items) < 0.95 and flags[5] == 0:
                print('********* 80%')
                flags[5] = 1
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
    print('Completed!\n{} new dummy-{} instances has been successfully created and add to db.'.format(items, c))
    print('Connection happened on : {}'.format(current_app.config['SQLALCHEMY_DATABASE_URI']))

# DATABASE OBJECTS STRUCTURE #


class USER(db.Model, UserMixin):
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
    about_me = db.Column(db.Text(250))
    city = db.Column(db.String, nullable=True)

    pswHash = db.Column(db.String(60), unique=False, nullable=False)    # stores hashed user password

    def fingerprint(self):
        print('USER :\n')
        for attr, value in self.__dict__.items():
            if not(attr.startswith('_') or attr.isupper()):     # print only public attributes of User class instance
                print("{} : {}\n".format(attr, value))

    def set_defaultImg(self):
        if self.sex != ('other' or None):
            if (type(self.sex) == bool) and self.sex:
                self.sex = 'male'
            else:
                self.sex = 'female'
            return str('default_' + self.sex + '_' + str(ceil(randint(1, 10) * random())) + '.jpg')
        else:
            return str('favicon.png')

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

    pub = db.relationship('Pub', uselist=False, backref='owners')  # creates one-to-one relationship between owner and his pub
    subsType = db.Column(db.String, nullable=False, default='free-acc') # stores hex codes whose refers to different acc-subscriptions
    subsExpirationDate = db.Column(db.DateTime, nullable=True)       # should be not nullable


class Pub(db.Model):
    __tablename__ = 'pubs'

    id = db.Column(db.Integer, primary_key=True)
    owner = db.relationship("Owner", backref="pubs")
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'))
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
    creation_date = db.Column(db.DateTime)  # creation date timestamp
    members = db.Column(db.Boolean)  # relationship thought group-subs association table
    watchlist = db.Column(db.Boolean)    # stores list of matches the group want to see this week


class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Binary, nullable=False)
    date = db.Column(db.DateTime)
    opponents = db.Column(db.String, nullable=False)    # stores the two teams who will play against each other


class Reservation(db.Model):
    """association table to solve users-to-pubs many-to-many relationship"""
    __tablename__ = 'reservations'

    QR_code = db.Column(db.String, primary_key=True)  # need to figure out how QR code can be stored
    booked_by = db.Column(db.Boolean)  # user.id backref
    booked_at = db.Column(db.Boolean)  # pub.id backref
    date = db.Column(db.DateTime)  # reservation timestamp
    seats = db.Column(db.Integer)  # number of people within the reservation
    confirmed = db.Column(db.Boolean)  # pub owner confirmation of the reservation


class Subscription(db.Model):
    """association table to solve users-to-groups many-to-many relationship"""
    __tablename__ = 'groups-subs'

    id = db.Column(db.Integer, primary_key=True)
    member = db.Column(db.Boolean)  # user.id backref
    group = db.Column(db.Boolean)  # group.id backref
    permissions = db.Column(db.String)  # user allowed actions in the group
    member_since = db.Column(db.DateTime)   # subscription timestamp
