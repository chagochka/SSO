from flask_wtf import FlaskForm
from wtforms import SubmitField


class AddForm(FlaskForm):
    submit = SubmitField('Добавить')
