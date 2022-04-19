from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField


class AdminForm(FlaskForm):
    user_id = StringField('id')
    submit = SubmitField('Забанить')
