from flask import url_for
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from teamgate.dbModel import User, Pub
from flask_login import current_user


class trialForm(FlaskForm):
    city = StringField('My place is in', validators=[DataRequired()])

    submit = SubmitField('Open the gate')


class registrationForm_user(FlaskForm):
    firstName = StringField('Name :', validators=[DataRequired()], render_kw={'placeholder':'Your firstname'})
    lastName = StringField('Surname :', validators=[DataRequired()], render_kw={'placeholder':'Your lastname'})
    city = StringField('You live in :', validators=[DataRequired()], render_kw={'placeholder':'City you live in'})
    sex = SelectField('Sex', validators=[DataRequired()], choices=[('male', 'male'), ('female', 'female'), ('other', 'none')])
    username = StringField('Choose an username :', validators=[DataRequired(), Length(min=2)], render_kw={'placeholder':'choose an username'})
    emailAddr = StringField('Email address :', validators=[DataRequired(), Email()], render_kw={'placeholder':'Active email address'})
    psw = PasswordField('Password :', validators=[DataRequired(), Length(min=8)], render_kw={'placeholder':'Choose a strong password'})
    confirmPsw = PasswordField('Confirm your Password :', validators=[DataRequired(), EqualTo('psw')], render_kw={'placeholder':'Confirm password'})

    submit = SubmitField('Complete registration!')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('This username ahs been already taken. Choose a different one.')

    def validate_emailAddr(self, emailAddr):
        if User.query.filter_by(email=emailAddr.data).first() or Pub.query.filter_by(email=emailAddr.data).first():
            raise ValidationError('An existing account is already linked to  this email address. Please use a different one.')


class registrationForm_pub(FlaskForm):
    username = StringField('Business name :', validators=[DataRequired()], render_kw={'placeholder':'Signboard of your business'})
    ownerFirstName = StringField('Owner Firstname :', validators=[DataRequired()], render_kw={'placeholder':'Your firstname'})
    ownerLastName = StringField('Owner Lastname :', validators=[DataRequired()], render_kw={'placeholder':'Your family name'})
    businessAddress = StringField('Address :', validators=[DataRequired()], render_kw={'placeholder':'address of your business'})
    city = StringField('You live in :', validators=[DataRequired()], render_kw={'placeholder':'Where your business is located'})
    businessDescription = TextAreaField('You live in :', validators=[DataRequired()], render_kw={'placeholder':'A brief description of who you are and what you do best'})
    seatsMax = IntegerField('Total seats you have :', validators=[DataRequired()], render_kw={'placeholder':'---'})
    subsType = SelectField('Type of subscription :', validators=[DataRequired()], choices=[('free', 'Free'), ('basic', 'Basic'), ('premium', 'Premium')])
    emailAddr = StringField('Email address :', validators=[DataRequired(), Email()], render_kw={'placeholder':'Active email address'})
    psw = PasswordField('Password :', validators=[DataRequired(), Length(min=8)], render_kw={'placeholder':'Choose a strong password'})
    confirmPsw = PasswordField('Confirm your Password :', validators=[DataRequired(), EqualTo('psw')], render_kw={'placeholder':'Confirm password'})


    submit = SubmitField('Complete registration!')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first() or Pub.query.filter_by(email=username.data).first():
            raise ValidationError('This username ahs been already taken. Choose a different one.')

    def validate_emailAddr(self, emailAddr):
        if User.query.filter_by(email=emailAddr.data).first() or Pub.query.filter_by(email=emailAddr.data).first():
            raise ValidationError('An existing account is already linked to  this email address. Please use a different one.')


class loginForm(FlaskForm):
    credential = StringField('Email address:\t', validators=[DataRequired(), Length(min=2)], render_kw={'placeholder':'Email address or Username'})
    psw = PasswordField('Password :\t', validators=[DataRequired(), Length(min=8)], render_kw={'placeholder':'Password'})
    rememberMe = BooleanField('Remember Me!')

    submit = SubmitField('Log me in!')


class accountDashboardForm(FlaskForm):
    firstName = StringField('Name :\t', validators=[DataRequired()])
    lastName = StringField('Surname :\t', validators=[DataRequired()])
    username = StringField('Username :\t', validators=[DataRequired(), Length(min=2)])
    emailAddr = StringField('Email address:\t', validators=[DataRequired(), Email()])
    img = FileField('Change profile pic', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Update profile')
    delete = SubmitField('Delete account', render_kw={"onclick": "url_for('deleteAccount')"})

    def validate_username(self, username):
        if username.data != current_user.username:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError('This username has been already used. Choose a different one.')

    def validate_emailAddr(self, emailAddr):
        if emailAddr.data != current_user.email:
            if User.query.filter_by(email=emailAddr.data).first() or Pub.query.filter_by(email=emailAddr.data).first():
                raise ValidationError('An existing account is already linked with  this email address. Please use a different one.')


class resetRequestForm(FlaskForm):
    emailAddr = StringField('Email address:\t', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset your password')

    def validate_emailAddr(self, emailAddr):
        if not(User.query.filter_by(email=emailAddr.data).first() or Pub.query.filter_by(email=emailAddr.data).first()):
            raise ValidationError('No existing accounts are linked with this email address.')


class resetPswForm(FlaskForm):
    psw = PasswordField('Password :', validators=[DataRequired(), Length(min=8)])
    confirmPsw = PasswordField('Confirm your Password :', validators=[DataRequired(), EqualTo('psw')])

    submit = SubmitField('Reset your password')

