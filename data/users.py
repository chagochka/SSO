"""Модель для работы с SQL-таблицей users"""

import datetime

import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .reports import Report
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
	"""Работа с информацией о пользователях"""

	__tablename__ = 'users'

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
	status = sqlalchemy.Column(sqlalchemy.String, nullable=True)
	about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
	email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
	hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
	created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

	reports = orm.relationship('Report', back_populates="users")

	def set_password(self, password):
		"""Создание хеша пароля"""
		self.hashed_password = generate_password_hash(password)

	def check_password(self, password):
		"""Проверка пароля"""
		return check_password_hash(self.hashed_password, password)

	def to_dict(self):
		"""Преобразование объекта User в словарь"""
		return {c.name: getattr(self, c.name) for c in self.__table__.columns if not c.name.startswith('_')}
