"""Сессия для работы с базой данных"""

import sqlalchemy as sa
import sqlalchemy.orm as orm  # Модуль, отвечающий за функциональность ORM.
from sqlalchemy.orm import Session  # Класс, отвечающий за соединение с базой данных.
import sqlalchemy.ext.declarative as dec  # Модуль для объявления (декларации) базы данных.


# Содаём абстрактную декларативную базу,
# от которой будем наследовать все наши модели:
SqlAlchemyBase = dec.declarative_base()

# Создаём фабрику подключений - это переменная,
# которую будем использовать для подключения сессий к базе данных.
__factory = None


def global_init(db_file):
    """Инициализация базы данных"""

    # Делаем фабрику подключений
    # глобально видимой:
    global __factory

    # Если фабрика уже создана и содержит какое-нибудь подключение,
    # то инициализацию повторно проводить не надо, выходим из фукции.
    if __factory:
        return

    # Проверяем правильность указания пути к базе данных:
    if not db_file or not db_file.strip():
        raise Exception('Необходимо указать файл базы данных.')

    # Создаем адрес подключения с параметрами для SQLAlchemy.
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f'Подключение к базе данных по адресу {conn_str}')

    # На основании полученных параметров,
    # Sqlalchemy выбирает подходящий движок (engine) для работы с базой данных:
    engine = sa.create_engine(conn_str, echo=False)
    # echo=True включит вывод в терминал всех генерируемых движком SQL-запросов.
    # Это может быть полезно при отладке.

    # Создаем фабрику подключений и биндим (связываем) её с движком engine:
    __factory = orm.sessionmaker(bind=engine)

    # Импортируем список моделей
    # с подавлением ошибки 'Unused import statement'
    # noinspection PyUnresolvedReferences
    from . import __all_models

    # Окончательно заставляем нашу базу данных создать все объекты,
    # которые она ещё не создала:
    SqlAlchemyBase.metadata.create_all(engine)


# Операция -> (стрелочка) делает явное указание типа возвращаемого функцией результата.
# В таком случае PyCharm начинает следить за событиями сессии, показывая полезные подсказки.
def create_session() -> Session:
    """Создание сессии подключения к базе данных"""
    global __factory
    return __factory()
