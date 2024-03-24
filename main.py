import datetime
import os

from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from flask import (
	Flask,
	render_template,
	request,
	make_response,
	session,
	jsonify,
	send_from_directory
)
from flask_login import (
	LoginManager,
	login_user,
	logout_user,
	login_required,
	current_user
)
from flask_restful import Api
from sqlalchemy import and_
from werkzeug.utils import redirect

from data import db_session, admin_api
from data.login import LoginForm
from data.register import RegisterForm
from data.report_resourses import ReportResource, ReportsList
from data.reports import Report
from data.users import User

UPLOAD_FOLDER = 'reports'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex_lyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)

if not os.path.exists(UPLOAD_FOLDER):
	os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ['docx']


def find_links(file):
	document = Document(file)
	rels = document.part.rels
	links = 0

	for rel in rels:
		if rels[rel].reltype == RT.HYPERLINK:
			links += 1

	return links


@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
	return make_response(jsonify({'error': 'Bad Request'}), 400)


@login_manager.user_loader
def load_user(user_id):
	"""Загрузка пользователя"""
	db = db_session.create_session()
	return db.get(User, user_id)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/')
@app.route('/index')
def index():
	"""Корневая страница"""
	return render_template('index.html')


@login_required
@app.route('/upload', methods=['GET', 'POST'])
def upload():
	"""Страница для отправки отчёта"""

	if request.method == 'POST':
		if 'file' not in request.files:
			return 'No file part', 400
		file = request.files['file']
		if file.filename == '':
			return 'No selected file', 400
		if file and allowed_file(file.filename):
			# filename = secure_filename(file.filename)
			if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], current_user.name)):
				os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], current_user.name))

			tmp = os.path.join(app.config['UPLOAD_FOLDER'], current_user.name)
			date = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
			path = os.path.join(str(tmp), f'{date}.docx')
			file.save(path)

			report = Report()
			report.author_id = current_user.id
			report.path = path
			report.points = 0
			report.status = 'Не проверено'
			report.links = find_links(path)
			db.add(report)
			db.commit()

			return render_template('upload.html', message='Отчёт успешно отправлен')
	# return redirect(url_for('uploaded_file', filename=filename))

	return render_template('upload.html')


# URL http://localhost:5000/register
@app.route('/register', methods=['GET', 'POST'])
def reqister():
	"""Страница регистрации"""
	db = db_session.create_session()

	regform = RegisterForm()
	users = db.query(User).filter(User.status == 'Учащийся').all()
	regform.full_name.choices = [
		(f'{user.surname} {user.name} {user.patronymic}', f'{user.surname} {user.name} {user.patronymic}') for user in
		users if not user.email]
	if regform.validate_on_submit():
		if regform.password.data != regform.password_again.data:
			return render_template('register.html',
			                       title='Регистрация',
			                       form=regform,
			                       message='Пароли не совпадают')
		if db.query(User).filter(User.email == regform.email.data).first():
			return render_template('register.html',
			                       title='Регистрация',
			                       form=regform,
			                       message='Такой пользователь уже есть')

		surname, name, patronymic = regform.full_name.data.split()

		user = db.query(User).filter(and_(
			User.surname == surname, User.name == name, User.patronymic == patronymic)).first()
		user.email = regform.email.data
		user.status = 'Учащийся'
		user.about = regform.about.data
		user.set_password(regform.password.data)
		db.commit()
		return redirect('/login')
	return render_template(
		'register.html',
		title='Регистрация',
		form=regform
	)


# URL http://localhost:5000/session_count_1
@app.route('/session_count_1')
def session_count_1():
	"""Счётчик посещений страницы (способ cookie)"""
	visits = request.cookies.get('visits_count', type=int)
	if visits:
		response = make_response(f'Количество посещений этой страницы: {visits + 1}')
		response.set_cookie('visits_count', str(visits + 1), max_age=60 * 60 * 24 * 365 * 3)
	else:
		response = make_response('Здравствуйте! Вы пришли на эту страницу в первый раз, '
		                         'или же заходили так давно, что мы о вас почти забыли;)')
		response.set_cookie('visits_count', '1', max_age=60 * 60 * 24 * 365 * 3)
	return response


# URL http://localhost:5000/session_count_2
@app.route('/session_count_2')
def session_count_2():
	"""Счётчик посещений страницы (способ session)"""
	if 'visits_count' in session:
		session['visits_count'] = session.get('visits_count') + 1
		visits = session['visits_count']
		response = make_response(f'Количество посещений этой страницы: {visits}')
	else:
		session['visits_count'] = 1
		response = make_response('Здравствуйте! Вы пришли на эту страницу в первый раз, '
		                         'или же заходили так давно, что мы о вас почти забыли;)')
	return response


# URL http://localhost:5000/login
@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Авторизация"""
	form = LoginForm()
	if form.validate_on_submit():
		db = db_session.create_session()
		user = db.query(User).filter(User.email == form.email.data).first()
		if user and user.check_password(form.password.data):
			login_user(user, remember=form.remember_me.data)
			return redirect("/")
		return render_template(
			'login.html',
			message="Неправильный логин или пароль",
			form=form
		)
	return render_template(
		'login.html',
		title='Авторизация',
		form=form
	)


@app.route('/user/<user_login>')
def search_user(user_login):
	"""Страница пользователя"""
	user = db.query(User).filter(User.email == user_login).first()
	user_reports_list = db.query(Report).filter(Report.id == user.id).all()
	return render_template('user_account_form.html', user=user, reports=user_reports_list)


# URL http://localhost:5000/logout
@app.route('/logout')
@login_required
def logout():
	"""Выход из аккаунта"""
	logout_user()
	return redirect('/')


if __name__ == '__main__':
	db_session.global_init('db/db.sqlite')
	db = db_session.create_session()
	if not list(db.query(User).filter(User.status == 'admin')):
		admin = User()
		admin.name = input('Введите своё имя: ')
		admin.email = input('Введите свою почту: ')
		admin.status = 'admin'
		admin.about = 'admin'
		admin.set_password(input('Установите пароль: '))
		db.add(admin)
		db.commit()
	app.register_blueprint(admin_api.blueprint)
	api.add_resource(ReportsList, '/api/reports')
	api.add_resource(ReportResource, '/api/reports/<int:reports_id>')
	app.run(host='localhost')
