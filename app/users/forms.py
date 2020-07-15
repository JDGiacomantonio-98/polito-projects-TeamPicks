from flask_login import current_user
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, MultipleFileField, IntegerField
from wtforms.validators import DataRequired, Length, Email, ValidationError

from app.dbModels import User, Owner, Group
from app.auth.methods import verify_psw

# it should be checked if the validate_field form method can already return the query result if not empty (!!)


class SearchItemsForm(FlaskForm):
	searchedItem = StringField(render_kw={'placeholder': 'Search for a group or a friend here!', 'class': 'form-control w-100'})

	submit = SubmitField('Search', render_kw={'class': 'btn btn-outline-info'})


class ProfileDashboardForm(FlaskForm):
	firstName = StringField('Name :', validators=[DataRequired(), Length(max=30)], render_kw={'class': 'form-control'})
	lastName = StringField('Surname :', validators=[DataRequired(), Length(max=50)], render_kw={'class': 'form-control'})
	username = StringField('Username :', validators=[DataRequired(), Length(min=2)], render_kw={'class': 'form-control'})
	email = StringField('Email address :', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Active email address', 'class': 'form-control'})
	submit = SubmitField('UPDATE', render_kw={'class': 'btn btn-info btn-sm mr-1'})
	delete = SubmitField('DELETE ACCOUNT', render_kw={'type': 'button',
													  'data-toggle': 'modal',
													  'data-target': '#delete-account-backdrop',
													  'class': 'btn btn-danger btn-sm'
													  })

	def validate_firstName(self, firstName):
		self.firstName.data = firstName.data.lower()

	def validate_lastName(self, lastName):
		self.lastName.data = lastName.data.lower()

	def validate_username(self, username):
		if len(self.username.data) > 15:
			raise ValidationError('Choose a shorter username (max length: 15chars)')
		if current_user.username != self.username.data:
			query = [User.query.filter_by(username=username.data).first(), Owner.query.filter_by(username=username.data).first()]
			if query[0] or query[1]:
				raise ValidationError('This username has been already taken. Choose a different one.')

	def validate_email(self, email):
		if current_user.email != self.email.data:
			query = [User.query.filter_by(email=email.data).first(), Owner.query.filter_by(email=email.data).first()]
			if query[0] or query[1]:
				raise ValidationError('This email address has been already taken. Choose a different one.')


class UploadProfileImgForm(FlaskForm):
	img = FileField('update your profile image', validators=[FileAllowed(['jpeg', 'jpg', 'png'])], render_kw={'class': 'w-100'})
	about_me = TextAreaField('About me', validators=[Length(max=250)], render_kw={'class': 'form-control',
																				 'rows': '12'})
	upload_img = SubmitField('upload', render_kw={'class': 'btn btn-outline-dark btn-sm w-100'})
	modify_about_me = SubmitField('modify', render_kw={'class': 'btn btn-outline-dark btn-sm'})

	def validate_about_me(self, about_me):
		self.about_me.data = about_me.data.lower()


class UploadProfileCarouselForm(FlaskForm):
	images = MultipleFileField('', validators=[FileAllowed(['jpeg', 'jpg', 'png'])])
	upload_carousel = SubmitField('upload new')

	def validate_images(self, images):
		if len(self.images.data) > 8:
			raise ValidationError('You can upload up-to 8 images')


class DeleteAccountForm(FlaskForm):
	psw = PasswordField('', validators=[DataRequired(), Length(min=8)], render_kw={'placeholder': 'password'})
	confirm_delete = SubmitField('Permanently delete my account')

	def validate_psw(self, psw):
		if not verify_psw(current_user.hash, psw.data):
			raise ValidationError('Uncorrect password.')


class CreateGroupForm(FlaskForm):
	name = StringField('Name:', validators=[DataRequired(), Length(min=10, max=100)], render_kw={'placeholder': 'your group name'})

	submit = SubmitField('Create it now!')

	def validate_name(self, name):
		if Group.query.filter_by(name=name).first():
			raise ValidationError('Ouch! you need to be more creative : this group already exist, choose another name.')


class CreatePubForm(FlaskForm):
	name = StringField('Your amazing pub name :', validators=[DataRequired(), Length(max=50)])
	address = StringField('Street address :', validators=[DataRequired()])
	phone_num = StringField('Phone number :', validators=[DataRequired(), Length(min=10, max=20)])
	seats_max = IntegerField('Please select your maximum amount of seats :', validators=[DataRequired()])
	description = TextAreaField('A brief description of your pub', render_kw={'placeholder': 'what do you do the best ? Tell it here to your customers!'})

	submit = SubmitField('Create pub')

	def validate_seats_max(self, seats_max):
		if not seats_max.data.is_numeric():
			raise ValidationError('Input a numeric value.')