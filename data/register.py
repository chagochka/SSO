"""Модель для регистрационной формы"""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, SelectField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField('Немного о себе')
    status = SelectField('Статус', choices=[('Преподаватель', 'Преподаватель'), ('Студент', 'Студент')], default='Преподаватель')
    submit = SubmitField('Войти')
