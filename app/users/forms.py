from flask import flash
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from app.dbModels import User, Owner, Group
from flask_login import current_user

# it should be checked if the validate_field form method can already return the query result if not empty (!!)


class registrationForm_user(FlaskForm):
    firstName = StringField('Name :', validators=[DataRequired()], render_kw={'placeholder':'Your firstname'})
    lastName = StringField('Surname :', validators=[DataRequired()], render_kw={'placeholder':'Your lastname'})
    username = StringField('Choose an username :', validators=[DataRequired(), Length(min=2)], render_kw={'placeholder': 'choose an username'})
    city = StringField('You live in :', validators=[DataRequired()], render_kw={'placeholder': 'City you live in'})
    sex = SelectField('Sex', validators=[DataRequired()], choices=[('m', 'male'), ('f', 'female'), ('other', 'none')])
    emailAddr = StringField('Email address :', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Active email address'})
    psw = PasswordField('Password :', validators=[DataRequired(), Length(min=8)], render_kw={'placeholder': 'Choose a strong password'})
    confirmPsw = PasswordField('Confirm your Password :', validators=[DataRequired(), EqualTo('psw')], render_kw={'placeholder': 'Confirm password'})

    submit = SubmitField('Complete registration!')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first() or Owner.query.filter_by(username=username.data).first():
            raise ValidationError('This username has been already taken. Choose a different one.')

    def validate_emailAddr(self, emailAddr):
        if User.query.filter_by(email=emailAddr.data).first() or Owner.query.filter_by(email=emailAddr.data).first():
            raise ValidationError('This email address has been already taken. Choose a different one.')


class registrationForm_pub(FlaskForm):
    username = StringField('Business name :', validators=[DataRequired()], render_kw={'placeholder':'Signboard of your business'})
    ownerFirstName = StringField('Owner Firstname :', validators=[DataRequired()], render_kw={'placeholder':'Your firstname'})
    ownerLastName = StringField('Owner Lastname :', validators=[DataRequired()], render_kw={'placeholder':'Your family name'})
    businessAddress = StringField('Address :', validators=[DataRequired()], render_kw={'placeholder':'address of your business'})
    city = StringField('You live in :', validators=[DataRequired()], render_kw={'placeholder':'Where your business is located'})
    businessDescription = TextAreaField('You live in :', validators=[DataRequired()], render_kw={'placeholder':'A brief description of who you are and what you do best'})
    seatsMax = IntegerField('Total seats you have :', validators=[DataRequired()], render_kw={'placeholder':'---'})
    subsType = SelectField('Type of subscription :', validators=[DataRequired()], choices=[('free', 'Free'), ('basic', 'Basic'), ('premium', 'Premium')])
    emailAddr = StringField('Email address :', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Active email address'})
    psw = PasswordField('Password :', validators=[DataRequired(), Length(min=8)], render_kw={'placeholder': 'Choose a strong password'})
    confirmPsw = PasswordField('Confirm your Password :', validators=[DataRequired(), EqualTo('psw')], render_kw={'placeholder': 'Confirm password'})

    submit = SubmitField('Complete registration!')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first() or Owner.query.filter_by(username=username.data).first():
            raise ValidationError('This username has been already taken. Choose a different one.')

    def validate_emailAddr(self, emailAddr):
        if User.query.filter_by(email=emailAddr.data).first() or Owner.query.filter_by(email=emailAddr.data).first():
            raise ValidationError('This email address has been already taken. Choose a different one.')


class accountDashboardForm(FlaskForm):
    img = FileField('Change profile pic', validators=[FileAllowed(['jpg', 'png'])])
    firstName = StringField('Name :', validators=[DataRequired()])
    lastName = StringField('Surname :', validators=[DataRequired()])
    username = StringField('Username :', validators=[DataRequired(), Length(min=2)])
    emailAddr = StringField('Email address :', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Active email address'})

    submit = SubmitField('Update profile')
    delete = SubmitField('Delete account', render_kw={'type': 'button',
                                                      'data-toggle': 'modal',
                                                      'data-target': '#delete-account-backdrop',
                                                      })

    def validate_username(self, username):
        if len(self.username.data) > 1:
            if current_user.username != self.username.data:
                query = [User.query.filter_by(username=username.data).first(), Owner.query.filter_by(username=username.data).first()]
                if query[0] or query[1]:
                    raise ValidationError('This username has been already taken. Choose a different one.')

    def validate_emailAddr(self, emailAddr):
        if current_user.email != self.emailAddr.data:
            query = [User.query.filter_by(email=emailAddr.data).first(), Owner.query.filter_by(email=emailAddr.data).first()]
            if query[0] or query[1]:
                raise ValidationError('This email address has been already taken. Choose a different one.')


class loginForm(FlaskForm):
    credential = StringField('Email address:', validators=[DataRequired(), Length(min=2)], render_kw={'placeholder':'Email address or Username'})
    psw = PasswordField('Password :', validators=[DataRequired(), Length(min=8)], render_kw={'placeholder':'Password'})
    rememberMe = BooleanField('Remember Me!')

    submit = SubmitField('Log me in!')


class resetPswForm(FlaskForm):
    psw = PasswordField('Password :', validators=[DataRequired(), Length(min=8)], render_kw={'placeholder': 'New password'})
    confirmPsw = PasswordField('Confirm your Password :', validators=[DataRequired(), EqualTo('psw')], render_kw={'placeholder': 'Confirm your password'})

    submit = SubmitField('Reset your password')


class createGroupForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired(), Length(min=10, max=100)], render_kw={'placeholder': 'your group name'})

    submit = SubmitField('Create it now!')

    def validate_name(self, name):
        if Group.query.filter_by(name=name):
            raise ValidationError('Ouch! you need to be more creative : this group already exist, choose another name.')
