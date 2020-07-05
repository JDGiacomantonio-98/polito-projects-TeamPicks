# DATABASE OBJECT CLASS SPECIFICATION MODULE : SQLAlchemy builds Object-Oriented Databases
from math import ceil
from random import randint, random
from datetime import datetime, timedelta

from flask import session, current_app, url_for
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as timedTokenizer
from faker import Faker
from sqlalchemy.exc import IntegrityError, OperationalError

from app import db, login_handler


# DATABASE GLOBAL FUNCTIONS #


def dummy(return_obj=True, model=None, items=1, w_test=False, feedback=True):
	from app.users.methods import hash_psw

	if type(return_obj) != bool:
		print('ERROR : single parameter only accepts bool')
		return None
	if model is None:
		print(f'Dummy objects to create : {items}\n')
		model = str(input('Which type of object do you want to create?\n'
						  '[U]ser\n'
						  '[O]wner\n'
						  '[P]ub\n'
						  '[G]roup\n'
						  '[M]atch\n\n'
						  '[Q]uit\n'
						  'select here : ')).lower()
	if model == 'q' or model == '':
		print('dummy() has been quited.')
		return None
	if w_test or return_obj:
		feedback = False
	if feedback:
		print('Please wait while processing dummy units ... (this might take a while)\n')
		progress = {
			0.10: 'completed : |*.............|',
			0.20: 'completed : |***...........| (20%)',
			0.30: 'completed : |****..........| (30%)',
			0.50: 'completed : |*******.......| (50%)',
			0.60: 'completed : |********......| (60%)',
			0.75: 'completed : |*********.....| (75%)',
			0.90: 'completed : |************..| (90%)'
		}
		errors = 0
		start = datetime.now()
		print('completed : |..............|')
	rand = Faker()
	i = 0
	while i < items:
		if model == 'u' or model == 'users':
			itm = User(username=rand.user_name(),
					   email=rand.email(),
					   lastSession=rand.past_date(),
					   firstName=rand.first_name(),
					   lastName=rand.last_name(),
					   age=randint(16, 90),
					   sex=rand.null_boolean(),
					   about_me=rand.text(max_nb_chars=250),
					   city=rand.city(),
					   pswHash=hash_psw('password')
					   )
			if itm.sex:
				itm.sex = 'm'
			elif itm.sex is not None:
				itm.sex = 'f'
			else:
				itm.sex = 'other'
			itm.set_defaultImg()
			model = 'users'
		elif model == 'o' or model == 'owners':
			itm = Owner(username=rand.user_name(),
						email=rand.email(),
						lastSession=rand.past_date(),
						firstName=rand.first_name(),
						lastName=rand.last_name(),
						age=randint(18, 90),
						sex=rand.null_boolean(),
						about_me=rand.text(max_nb_chars=250),
						city=rand.city(),
						pswHash=hash_psw('password'),
						subsType=f"{randint(0, 3):02b}",
						subsExpirationDate=rand.future_date('+90d')
						)
			if rand.boolean(chance_of_getting_true=70):
				pub = dummy(model='p', w_test=w_test)
				itm.associate_pub(pub)
			model = 'owners'
		elif model == 'p' or model == 'pubs':
			seatsMax = randint(0, 200)
			itm = Pub(address=rand.address(),
					  bookable=rand.boolean(chance_of_getting_true=50),
					  seatsMax=seatsMax,
					  rating=randint(0, 5),
					  description=rand.text(max_nb_chars=500))
			if itm.bookable:
				itm.seatsBooked = seatsMax - randint(0, seatsMax)
			model = 'pubs'
		elif model == 'g' or model == 'groups':
			itm = Group(name=rand.sentence(nb_words=8))
			model = 'groups'
		elif model == 'm' or model == 'matches':
			print('We are sorry but this function is still under development!')
			itm = Match()
			model = 'matches'
		if not return_obj:
			db.session.add(itm)
			try:
				db.session.commit()
				if w_test:
					db.session.delete(itm)
					db.session.commit()
				i += 1
			except IntegrityError:
				db.session.rollback()
				if feedback:
					errors += 1
			except OperationalError as e:
				print('(!) INFO : Have you run upgrade() from last migration file?')
				if w_test:
					raise RuntimeError
				else:
					return e
			except BaseException:
				raise RuntimeError
			if feedback:
				try:
					print(progress[round((i / items), 2)])
				except KeyError:
					pass
		else:
			return itm
	if feedback:
		print(
			f'Completed!\n{items} new dummy-{model} instances has been successfully created and add to db. ({errors} errors occurred and have been corrected)')
		print(f'Connection happened on : {current_app.config["SQLALCHEMY_DATABASE_URI"]}')
		print(f'Process duration : {datetime.now() - start}')


@login_handler.user_loader
def load_user(user_id):
	if session.get('dbModelType') == 'user':
		return User.query.get(user_id)
	else:
		return Owner.query.get(user_id)


# DATABASE OBJECTS STRUCTURE #
"""

(!) NOTE: there is no need to explicitly define a __init__ method on model classes.
That’s because SQLAlchemy adds an implicit constructor to all model classes which accepts keyword arguments for all its 
columns and relationships. If you decide to override the constructor for any reason, make sure to keep accepting **kwargs 
and call the super constructor with those **kwargs to preserve this behavior
"""


class Reservation(db.Model):
	"""association table to solve users-to-pubs many-to-many relationship"""
	__tablename__ = 'reservations'

	code = db.Column(db.Integer,  # need to figure out how QR code can be stored
					 primary_key=True,
					 index=True)
	date = db.Column(db.DateTime, default=datetime.now(), index=True)  # reservation timestamp
	guests = db.Column(db.Integer)  # number of people within the reservation
	confirmed = db.Column(db.Boolean, default=False, index=True)  # pub owner confirmation of the reservation
	by_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)  # user.id foreignKey
	at_id = db.Column(db.Integer, db.ForeignKey('pubs.id'), index=True, nullable=False)  # pub.id foreignKey


class Subscription(db.Model):
	"""association table to solve users-to-groups many-to-many relationship"""
	__tablename__ = 'groups_subs'

	id = db.Column(db.Integer,
				   primary_key=True)
	member_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)  # user.id foreignKey
	group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), index=True, nullable=False)  # group.id backref
	role_id = db.Column(db.Integer, db.ForeignKey('group_roles.id'),
						nullable=False)  # user allowed actions in the group
	member_since = db.Column(db.DateTime, default=datetime.utcnow())  # subscription timestamp


class USER:
	id = db.Column(db.Integer,
				   primary_key=True)
	username = db.Column(db.String(15),
						 unique=True,
						 nullable=False,
						 index=True)
	email = db.Column(db.String,
					  unique=True,
					  nullable=False,
					  index=True)
	confirmed = db.Column(db.Boolean,
						  nullable=False,
						  default=False)
	lastSession = db.Column(db.DateTime,
							nullable=False,
							default=datetime.utcnow())
	member_since = db.Column(db.DateTime,
							 nullable=False,
							 default=datetime.utcnow())
	firstName = db.Column(db.String(60),
						  nullable=False)
	lastName = db.Column(db.String(60),
						 nullable=False)
	age = db.Column(db.Integer)
	sex = db.Column(db.String, default='other')
	img = db.Column(db.String)  # stores the filename string of the img file
	about_me = db.Column(db.Text(250))
	city = db.Column(db.String)
	pswHash = db.Column(db.String(60),  # stores hashed user password
						unique=False,
						nullable=False)

	def __str__(self):
		fingerprint = 'INFO :\n'
		for attr, value in self.__dict__.items():
			if not (attr.startswith('_') or attr.isupper()):  # retrieve only public attributes of User class instance
				fingerprint += f"| {attr} -->\t{value}\n"
		return fingerprint

	def set_defaultImg(self):
		if self.sex != 'other':
			self.img = f'def-{self.sex}-{str(ceil(randint(1, 10) * random()))}.jpg'
		else:
			# create Gravatar instead
			self.img = 'favicon.png'

	def get_imgFile(self):
		if ('def-' in self.img) or (self.img == 'favicon.png'):
			return url_for('static', filename='profile_pics/AVATAR/' + self.img)
		else:
			return url_for('static', filename='profile_pics/users/' + self.img)

	def create_token(self, expireInSec=(8 * 60)):
		return timedTokenizer(current_app.config['SECRET_KEY'], expireInSec).dumps({'load': self.id}).decode('utf-8')

	def has_permission_to(self, action):
		pass


class User(db.Model, UserMixin, USER):
	__tablename__ = 'users'

	sports = db.Column(db.Boolean)  # relationship
	groups = db.relationship('Subscription',
							 foreign_keys=[Subscription.member_id],
							 backref=db.backref('member', lazy='joined'),
							 lazy='dynamic',
							 cascade='all, delete-orphan')
	reservations = db.relationship('Reservation',
								   foreign_keys=[Reservation.by_id],
								   backref=db.backref('made_by', lazy='joined'),
								   # adds <made_by> parameter to Reservation model : gain complete access user object
								   lazy='dynamic',
								   cascade='all, delete-orphan')

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		self.set_defaultImg()

	def __repr__(self):
		return f'User {self.id} <{self.username}>'

	def join_as_admin(self, group):
		role = G_Role.query.filter_by(role='admin').first()
		print(role.id)
		itm = Subscription(group=group, member=self, role=role)
		db.session.add(itm)
		db.session.commit()

	def send_bookingReq(self, pub, guests):
		# information comes from form
		if pub.is_available_for(guests):
			tempRes = pub.cache_bookingReq(booked_by=self, guests=guests)
			print(f'\nQR code : {tempRes.code}\nconfirmation status : {tempRes.confirmed}')  # debug

	def send_joinReq(self, group):  # group comes from query in view func
		pass

	def accept_joinReq(self):
		if self.has_permission_to(action='MANAGE_SUBS'):
			pass


class Owner(db.Model, UserMixin, USER):
	__tablename__ = 'owners'

	subsType = db.Column(db.String,
						 nullable=False,
						 default='free-acc')  # stores hex codes whose refers to different acc-subscriptions
	subsExpirationDate = db.Column(db.DateTime, default=None)
	pub = db.relationship('Pub',
						  uselist=False,  # force a one-to-one relationship between owner and his pub
						  backref='owner',
						  cascade='all, delete-orphan')

	def __init__(self, **kwargs):
		super(Owner, self).__init__(**kwargs)
		self.set_defaultImg()
		if self.member_since is None:
			self.member_since = datetime.utcnow()

	def __repr__(self):
		return f'Owner {self.id} <{self.username}>'

	def associate_pub(self, pub):  # pub object comes from form submission
		self.pub = pub

	def evaluate_subs(self):
		self.evaluate_expirationDate()
		try:
			if self.subsType != 'free-acc':
				self.pub.bookable = True
		except AttributeError:
			pass

	def evaluate_expirationDate(self):
		if self.subsExpirationDate is None:
			self.subsExpirationDate = self.member_since + timedelta(weeks=4)
		elif self.subsExpirationDate <= datetime.utcnow():

			from app.main.methods import check_subs_payment

			if check_subs_payment(self):
				self.subsExpirationDate += timedelta(weeks=4)

	def confirm_pub_reservation(self, res_id):
		# res = self.pub.reservations.query.filter_by(code=res_id).first()
		res = self.pub.reservations.query.all()
		print(res)
		res.confirmed = True
		print(res)


class Pub(db.Model):
	__tablename__ = 'pubs'

	id = db.Column(db.Integer, primary_key=True)
	owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'))
	address = db.Column(db.String,
						nullable=False)
	bookable = db.Column(db.Boolean,
						 nullable=False)
	seatsMax = db.Column(db.Integer,
						 nullable=False)
	seatsBooked = db.Column(db.Integer,
							nullable=False,
							default=0)
	rating = db.Column(db.Integer,
					   nullable=False,
					   default=0)
	description = db.Column(db.Text(500),
							nullable=True,
							default='let your customer know what you do best.')
	reservations = db.relationship('Reservation',
								   foreign_keys=[Reservation.at_id],
								   backref=db.backref('at', lazy='joined'),
								   # adds <at> parameter to Reservation model : gain complete access pub object
								   lazy='dynamic',
								   cascade='all, delete-orphan')

	def get_address(self):
		return self.address

	def get_rating(self):
		return self.rating

	def get_description(self):
		return self.description

	def get_availability(self):
		return self.seatsMax - self.seatsBooked

	def notify(self, eventType, item=None):
		# here we should notify Owner of the incoming request in order to let him accept it or not
		# item represent notification body object
		print(f'Owner id : {self.owner_id}')
		if eventType == 'new-booking':
			pass

	def is_available_for(self, guests):
		if self.bookable:
			if self.get_availability() >= guests:
				return True
			else:
				print('Impossible to schedule a reservation for that date.')
				print(f'Free tables : {self.get_availability()}')
		else:
			print("This pub can not accepts reservation yet!")
			return False

	def cache_bookingReq(self, booked_by, guests):
		tempRes = Reservation(made_by=booked_by,
							at=self,
							guests=guests)
		db.session.add(tempRes)
		db.session.commit()
		self.notify(eventType='new-booking', item=tempRes)
		return tempRes

	def book_for(self, guests):
		self.seatsBooked += guests


class Group(db.Model):
	__tablename__ = 'groups'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(15),
					 unique=True,
					 nullable=False)
	creation_date = db.Column(db.DateTime, default=datetime.utcnow())  # creation date timestamp
	subs = db.relationship('Subscription',
						foreign_keys=[Subscription.group_id],
						backref=db.backref('group', lazy='joined'),
						lazy='dynamic',
						cascade='all, delete-orphan')  # relationship thought group-subs association table
# watchlist = db.Column(db.Boolean)  # stores list of matches the group want to see this week


class G_PERMISSIONS:
	def __init__(self):
		self.POST = 1
		self.MODIFY = 2  # modify group topic and image
		self.MODERATE = 4  # moderate member contents
		self.SET_FLAGS = 8  # flag the group as 'accepting pub offers'
		self.MANAGE_SUBS = 16  # add/remove members

	def admin(self):
		ADMIN = 0
		for a, v in self.__dict__.items():
			if a.isupper():
				ADMIN += v
		return ADMIN

	def member(self):
		return self.POST

	def moderator(self):
		return self.member() + self.MODERATE + self.MODIFY

	def manager(self):
		return self.member() + self.SET_FLAGS + self.MANAGE_SUBS


class G_Role(db.Model):
	__tablename__ = 'group_roles'

	id = db.Column(db.Integer, primary_key=True)
	role = db.Column(db.String, unique=True)
	is_default = db.Column(db.Boolean, default=False, index=True)
	permissions = db.Column(db.Integer, default=0)
	users = db.relationship('Subscription',
							foreign_keys=[Subscription.role_id],
							backref=db.backref('role', lazy='joined')
							)

	def __init__(self, **kwargs):
		super(G_Role, self).__init__(**kwargs)
		if self.permissions is None:
			self.reset_permission()

	def add_permission(self, permission):
		self.permissions += permission

	def remove_permission(self, permission):
		self.permissions -= permission

	def reset_permission(self):
		self.permissions = 0


class Match(db.Model):
	__tablename__ = 'matches'

	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.Binary,
					 nullable=False)
	date = db.Column(db.DateTime)
	opponents = db.Column(db.String,
						  nullable=False)  # stores the two teams who will play against each other
