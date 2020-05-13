from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class trialForm(FlaskForm):
    city = StringField('My place is in', validators=[DataRequired()])

    submit = SubmitField('Open the gate')

