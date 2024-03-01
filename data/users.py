"""Модель для работы с SQL-таблицей users"""

import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    """Работа с информацией о пользователях"""
    
    # Задаём имя таблицы:
    __tablename__ = 'users'

    # Задаём столбцы таблицы users:
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    # Сообщения пользователя.
    # Используем метод relation(),
    # который связывает новость с конкретным пользователем:
    # news = orm.relationship('News')
    # Эта строка связана со строкой из файла news.py --> user = orm.relation('User')

    # Хранить пароль в открытом виде нельзя, поэтому во Flask есть инструменты,
    # которые позволяют создавать хеши паролей. При вводе пароля происходит его проверка
    # на соответствие значению хеша, хранимого в базе данных.

    def set_password(self, password):
        """Создание хеша пароля"""
        # Функция используется при регистрации пользователя.
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        """Проверка пароля"""
        # Смотрим, соответствует ли пароль значению хеша на сервере:
        return check_password_hash(self.hashed_password, password)
