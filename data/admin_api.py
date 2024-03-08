from functools import wraps

from flask import jsonify, make_response, Blueprint, current_app, render_template
from flask_login import login_required, current_user
from requests import get

from . import db_session
from .users import User

blueprint = Blueprint(
	'admin_api',
	__name__,
	template_folder='templates'
)


def admin_required(f):
	@wraps(f)
	@login_required
	def decorated_function(*args, **kwargs):
		with current_app.test_request_context():
			if current_user.status == "admin":
				return f(*args, **kwargs)
			else:
				return make_response(jsonify({'error': 'Отказано в доступе'}), 400)

	return decorated_function


@blueprint.route('/admin/dashboard')
@admin_required
def dashboard():
	db_sess = db_session.create_session()
	users = db_sess.query(User).filter(User.status == 'Учащийся')
	users_list = [user.to_dict() for user in users]
	return render_template('admin_dashboard.html', users=users_list)


@blueprint.route('/admin/users')
@admin_required
def get_users():
	db_sess = db_session.create_session()
	users = db_sess.query(User).filter(User.status == 'Учащийся')
	return jsonify(
		{
			'users':
				[item.to_dict() for item in users]
		}
	)


@blueprint.route('/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def get_one_user(user_id):
	db_sess = db_session.create_session()
	user = db_sess.query(User).get(user_id)
	if not user:
		return make_response(jsonify({'error': 'Not found'}), 404)
	return jsonify(
		{
			'user': user.to_dict()
		}
	)


@blueprint.route('/admin/search_user', methods=['POST'])
@login_required
def search_user():
    # username = request.form['username']
    # # Здесь должна быть логика поиска пользователя по имени
    # # Например, получение пользователя из базы данных по имени
    # user = User.query.filter_by(username=username).first()
    # if user:
    #     # Обработка результатов поиска, например, перенаправление на страницу пользователя
    #     return redirect(url_for('user_profile', user_id=user.id))
    # else:
    #     # Обработка случая, когда пользователь не найден
    #     return "Пользователь не найден", 404
    pass

