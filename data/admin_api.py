import configparser
from collections import defaultdict
from datetime import datetime
from functools import wraps

from flask import jsonify, make_response, Blueprint, current_app, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from . import db_session
from .users import User

blueprint = Blueprint(
	'admin_api',
	__name__,
	template_folder='templates'
)

month_names_ru = {
	1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 5: "Май", 6: "Июнь", 7: "Июль", 8: "Август", 9: "Сентябрь",
	10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
}


def group_deadlines_by_month(deadlines):
	deadlines_by_month = defaultdict(list)
	for deadline in deadlines:
		deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
		month_year = month_names_ru[deadline_date.month] + " " + str(deadline_date.year)
		deadlines_by_month[month_year].append(deadline)

	return dict(
		sorted(deadlines_by_month.items(), key=lambda item: list(month_names_ru.values()).index(item[0].split()[0]))
	)


def get_users():
	db_sess = db_session.create_session()
	users = db_sess.query(User).filter(User.status == 'Волонтёр')
	return [user.to_dict() for user in users]


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
	return render_template('admin_dashboard.html', users=get_users(), title='Панель администратора')


@blueprint.route('/admin/users')
@admin_required
def get_users_request():
	return jsonify(
		{
			'users':
				get_users()
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


@blueprint.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
	if current_user.status != "admin":
		return make_response(jsonify({'error': 'Отказано в доступе'}), 400)

	db_sess = db_session.create_session()

	if request.method == 'POST':
		surname = request.form.get('surname')
		name = request.form.get('name')
		patronymic = request.form.get('patronymic')

		user = User()
		user.surname = surname
		user.name = name
		user.patronymic = patronymic
		user.status = 'Волонтёр'

		db_sess.add(user)
		db_sess.commit()
		return redirect('/admin/dashboard')

	return render_template('add_user.html', title='Добавление волонтёра')


@blueprint.route('/admin/settings')
@admin_required
def settings():
	config = configparser.ConfigParser()
	config.read('settings.ini')

	deadlines = [config.get('deadlines', deadline) for deadline in config.options('deadlines')]
	deadlines_by_month = group_deadlines_by_month(deadlines)

	maxLinks = config.get('settings', 'maxLinks', fallback='30')
	minLinks = config.get('settings', 'minLinks', fallback='10')

	return render_template(
		'settings.html',
		deadlines=deadlines, deadlines_by_month=deadlines_by_month,
		maxLinks=maxLinks, minLinks=minLinks, title='Настройки'
	)


@blueprint.route('/admin/update_settings', methods=['POST'])
def update_settings():
	deadlines = request.form.getlist('deadlines[]')
	remove_deadline = request.form.getlist('remove_deadline')
	maxLinks = request.form.get('maxLinks')
	minLinks = request.form.get('minLinks')

	config = configparser.ConfigParser()
	config.add_section('deadlines')
	config.add_section('settings')

	config.set('settings', 'maxLinks', maxLinks)
	config.set('settings', 'minLinks', minLinks)

	added_dates = {}

	if remove_deadline:
		if config.has_option('deadlines', f'deadline{remove_deadline}'):
			print(f'deadline{remove_deadline}')
			config.remove_option('deadlines', f'deadline{remove_deadline}')
			with open('settings.ini', 'w') as configfile:
				config.write(configfile)

	for i, deadline in enumerate(deadlines, start=1):
		if deadline not in added_dates:
			config.set('deadlines', f'deadline{i}', deadline)
			added_dates[deadline] = True

	with open('settings.ini', 'w') as configfile:
		config.write(configfile)

	return redirect(url_for('admin_api.settings'))
