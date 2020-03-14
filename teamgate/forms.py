from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from teamgate.dbModel import User, Pub
from flask_login import current_user


class registrationForm(FlaskForm):
    isPub = BooleanField('I own a pub or a dining activity')
    firstName = StringField('Name :\t', validators=[DataRequired()])
    lastName = StringField('Surname :\t', validators=[DataRequired()])
    sex = SelectField('Sex', validators=[DataRequired()], choices=[('male', 'male'), ('female', 'female'), ('other', 'none')])
    username = StringField('Choose an username :\t', validators=[DataRequired(), Length(min=2)])
    emailAddr = StringField('Email address:\t', validators=[DataRequired(), Email()])
    psw = PasswordField('Password :\t', validators=[DataRequired(), Length(min=8)])
    confirmPsw = PasswordField('Confirm your Password :\t', validators=[DataRequired(), EqualTo('psw')])

    submit = SubmitField('Access your TeamGATE now!')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('This username ahs been already taken. Choose a different one.')

    def validate_emailAddr(self, emailAddr):
        if User.query.filter_by(email=emailAddr.data).first() or Pub.query.filter_by(email=emailAddr.data).first():
            raise ValidationError('An existing account is already linked to  this email address. Use a different one.')


class loginForm(FlaskForm):
    emailAddr = StringField('Email address:\t', validators=[DataRequired(), Email(), Length(min=2)])
    psw = PasswordField('Password :\t', validators=[DataRequired(), Length(min=8)])
    rememberMe = BooleanField('Remember Me!\t')

    submit = SubmitField('Log me in!')


class accountDashboardForm(FlaskForm):
    firstName = StringField('Name :\t', validators=[DataRequired()])
    lastName = StringField('Surname :\t', validators=[DataRequired()])
    username = StringField('Username :\t', validators=[DataRequired(), Length(min=2)])
    emailAddr = StringField('Email address:\t', validators=[DataRequired(), Email()])
    img = FileField('Change profile pic', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Update profile')

    def validate_username(self, username):
        if username.data != current_user.username:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError('This username has been already used. Choose a different one.')

    def validate_emailAddr(self, emailAddr):
        if emailAddr.data != current_user.email:
            if User.query.filter_by(email=emailAddr.data).first() or Pub.query.filter_by(email=emailAddr.data).first():
                raise ValidationError('An existing account is already linked with  this email address. Use a different one.')


class resetRequestForm(FlaskForm):
    emailAddr = StringField('Email address:\t', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset your password')

    def validate_emailAddr(self, emailAddr):
        if not(User.query.filter_by(email=emailAddr.data).first() or Pub.query.filter_by(email=emailAddr.data).first()):
            raise ValidationError('No existing accounts are linked with this email address.')


class resetPswForm(FlaskForm):
    psw = PasswordField('Password :\t', validators=[DataRequired(), Length(min=8)])
    confirmPsw = PasswordField('Confirm your Password :\t', validators=[DataRequired(), EqualTo('psw')])

    submit = SubmitField('Reset your password')