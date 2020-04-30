from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
from app.dbModels import Owner, User


class trialForm(FlaskForm):
    city = StringField('My place is in', validators=[DataRequired()])

    submit = SubmitField('Open the gate')


class resetRequestForm(FlaskForm):
    emailAddr = StringField('Email address:\t', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email address'})
    submit = SubmitField('Send request')

    def validate_emailAddr(self, emailAddr):
        if not(User.query.filter_by(email=emailAddr.data).first() or Owner.query.filter_by(email=emailAddr.data).first()):
            raise ValidationError('No existing accounts are linked with this email address.')