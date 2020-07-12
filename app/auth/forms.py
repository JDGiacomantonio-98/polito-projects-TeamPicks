from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError

from app.dbModels import User, Owner, Group


class RegistrationForm_base(FlaskForm):
	firstName = StringField('Name :', validators=[DataRequired()], render_kw={'placeholder':'Your firstname'})
	lastName = StringField('Surname :', validators=[DataRequired()], render_kw={'placeholder':'Your lastname'})
	username = StringField('Choose an username :', validators=[DataRequired(), Length(min=2)], render_kw={'placeholder': 'choose an username'})
	city = StringField('You live in :', validators=[DataRequired()], render_kw={'placeholder': 'City you live in'})
	sex = SelectField('Sex', validators=[DataRequired()], choices=[('m', 'male'), ('f', 'female'), ('other', 'none')])
	about_me = TextAreaField( render_kw={'placeholder': 'Tell to other about yourself! (in brief)'})
	email = StringField('Email address :', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Active email address'})
	psw = PasswordField('Password:', validators=[DataRequired(), Length(min=8)], render_kw={'placeholder': 'Choose a strong password'})
	confirmPsw = PasswordField('Confirm your Password :', validators=[DataRequired(), EqualTo('psw')], render_kw={'placeholder': 'Confirm password'})

	accept_terms = BooleanField('I accept all Terms and Condition agreement', validators=[DataRequired()])

	submit = SubmitField('Complete registration!')

	def validate_firstName(self, firstName):
		self.firstName.data = firstName.lower()

	def validate_lastName(self, lastName):
		self.lastName.data = lastName.lower()

	def validate_username(self, username):
		if len(self.username.data) > 15:
			raise ValidationError('Choose a shorter username (max length: 15chars)')
		if User.query.filter_by(username=username.data).first() or Owner.query.filter_by(username=username.data).first():
			raise ValidationError('This username has been already taken. Choose a different one.')

	def validate_city(self, city):
		self.city.data = city.lower()

	def validate_about_me(self, about_me):
		self.about_me.data = about_me.lower()

	def validate_email(self, email):
		if User.query.filter_by(email=email.data).first() or Owner.query.filter_by(email=email.data).first():
			raise ValidationError('This email address has been already taken. Choose a different one.')


class RegistrationForm_owner(RegistrationForm_base):
	subsType = SelectField('Type of subscription :', validators=[DataRequired()], choices=[('free', 'Free'), ('basic', 'Basic'), ('premium', 'Premium')])


class RegistrationForm_pub(FlaskForm):
	businessAddress = StringField('Address :', validators=[DataRequired()], render_kw={'placeholder': 'address of your business'})
	businessDescription = TextAreaField('You live in :', validators=[DataRequired()], render_kw={'placeholder': 'A brief description of who you are and what you do best'})
	seatsMax = IntegerField('Total seats you have :', validators=[DataRequired()], render_kw={'placeholder': '---'})

	submit = SubmitField('Complete registration!')


class LoginForm(FlaskForm):
	credential = StringField('Email address:', validators=[DataRequired(), Length(min=2)], render_kw={'placeholder':'Email address or Username'})
	psw = PasswordField('Password :', validators=[DataRequired(), Length(min=8)], render_kw={'placeholder':'password'})
	rememberMe = BooleanField('Remember Me!')

	submit = SubmitField('Log me in!')


class ResetRequestForm(FlaskForm):
	email = StringField('Email address:\t', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email address'})
	submit = SubmitField('Send request')

	def validate_email(self, email):
		if not(User.query.filter_by(email=email.data).first() or Owner.query.filter_by(email=email.data).first()):
			raise ValidationError('No existing accounts are linked with this email address.')


class ResetPswForm(FlaskForm):
	psw = PasswordField('Password :', validators=[DataRequired(), Length(min=8)], render_kw={'placeholder': 'New password'})
	confirmPsw = PasswordField('Confirm your Password :', validators=[DataRequired(), EqualTo('psw')], render_kw={'placeholder': 'Confirm your password'})

	submit = SubmitField('Reset your password')

