from flask import jsonify
from flask_restful import abort, Resource
from . import db_session
from .reports import Report


# Эту функцию логичнее перенести из miniblog.py сюда:
def not_found(report_id):
    """Проверка существования новости в базе данных"""
    db = db_session.create_session()
    report = db.query(Report).get(report_id)
    if not report:
        abort(404, message=f'News {report_id} not found')


class ReportResource(Resource):
    """Класс для работы с одной новостью"""

    # Некоторые методы классов не используют self для своей работы.
    # В этом случае PyCharm выдаёт ошибку серого цвета:
    # Method 'get' may be 'static' (Метод get может быть статическим)

    # В таком случае рекомендуется объявить метод статическим -
    # это экономит оперативную память.
    @staticmethod
    def get(report_id):
        """Смотрит одну новость из базы"""
        not_found(report_id)
        db = db_session.create_session()
        report = db.query(Report).get(report_id)
        return jsonify(
            {
                'reports': report.to_dict(
                )
            }
        )

    @staticmethod
    def delete(report_id):
        """Удаляет одну новость из базы"""
        not_found(report_id)
        db = db_session.create_session()
        report = db.query(Report).get(report_id)
        db.delete(report)
        db.commit()
        return jsonify({'success': 'OK'})


class ReportsList(Resource):
    """Класс для работы со списком новостей"""

    @staticmethod
    def get():
        """Смотрит список новостей в базе"""
        db = db_session.create_session()
        report = db.query(Report).all()
        return jsonify(
            {
                'reports': [item.to_dict() for item in report]
            }
        )

    @staticmethod
    def post():
        """Добавляет новость в список новостей"""
        db = db_session.create_session()
        report = Report()
        db.add(report)
        db.commit()
        return jsonify({'success': 'OK'})
