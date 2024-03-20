"""Модель для регистрационной формы"""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, SelectField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired

from . import db_session
from .users import User

db_session.global_init('db/db.sqlite')


class RegisterForm(FlaskForm):
	email = EmailField('Почта', validators=[DataRequired()])
	password = PasswordField('Пароль', validators=[DataRequired()])
	password_again = PasswordField('Повторите пароль', validators=[DataRequired()])

	def create_full_name(self):
		db_sess = db_session.create_session()
		users = db_sess.query(User).filter(User.status == 'Учащийся')

		self.full_name = SelectField('Полное имя', choices=[
			(f'{user.surname} {user.name} {user.patronymic}', f'{user.surname} {user.name} {user.patronymic}')
			for user in users if not user.email
		], validators=[DataRequired()])

	about = TextAreaField('Немного о себе')
	submit = SubmitField('Войти')
