# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional

class UsernameForm(FlaskForm):
    github_username = StringField('GitHub Username', validators=[Optional()])
    stackoverflow_username = StringField('Stack Overflow Username', validators=[Optional()])
    submit = SubmitField('Submit')
