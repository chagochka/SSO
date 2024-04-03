from flask import jsonify
from flask_restful import abort, Resource
from . import db_session
from .reports import Report


def not_found(report_id):
    """Проверка существования отчёта в базе данных"""
    db = db_session.create_session()
    report = db.query(Report).get(report_id)
    if not report:
        abort(404, message=f'News {report_id} not found')


class ReportResource(Resource):
    """Класс для работы с одним отчётом"""

    @staticmethod
    def get(report_id):
        """Смотрит один отчёт из базы"""
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
        """Удаляет один отчёт из базы"""
        not_found(report_id)
        db = db_session.create_session()
        report = db.query(Report).get(report_id)
        db.delete(report)
        db.commit()
        return jsonify({'success': 'OK'})


class ReportsList(Resource):
    """Класс для работы со списком отчётов"""

    @staticmethod
    def get():
        """Смотрит список отчётов в базе"""
        db = db_session.create_session()
        report = db.query(Report).all()
        return jsonify(
            {
                'reports': [item.to_dict() for item in report]
            }
        )

    @staticmethod
    def post():
        """Добавляет отчёт в список отчётов"""
        db = db_session.create_session()
        report = Report()
        db.add(report)
        db.commit()
        return jsonify({'success': 'OK'})
