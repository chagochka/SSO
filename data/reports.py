"""Модель для работы с SQL-таблицей reports"""

import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class Report(SqlAlchemyBase, UserMixin):
    """Работа с информацией о пользователях"""

    __tablename__ = 'reports'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    path = sqlalchemy.Column(sqlalchemy.Text)
    points = sqlalchemy.Column(sqlalchemy.Integer)
    status = sqlalchemy.Column(sqlalchemy.Text)
    links = sqlalchemy.Column(sqlalchemy.Integer)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    users = orm.relationship('User', back_populates="reports")

    def to_dict(self):
        """Преобразование объекта User в словарь"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if not c.name.startswith('_')}
