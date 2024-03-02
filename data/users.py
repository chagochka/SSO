"""Модель для работы с SQL-таблицей users"""

import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
	"""Работа с информацией о пользователях"""

	__tablename__ = 'users'

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
	status = sqlalchemy.Column(sqlalchemy.String, nullable=True)
	about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
	email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
	hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
	created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

	# news = orm.relationship('News')
	# Эта строка понадобится для свяи со строкой из др. файла ...py --> user = orm.relation('User')

	def set_password(self, password):
		"""Создание хеша пароля"""
		self.hashed_password = generate_password_hash(password)

	def check_password(self, password):
		"""Проверка пароля"""
		return check_password_hash(self.hashed_password, password)
