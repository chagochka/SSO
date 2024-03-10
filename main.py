import datetime

from flask import (
	Flask,
	render_template,
	request,
	make_response,
	session,
	jsonify
)
from flask_login import (
	LoginManager,
	login_user,
	logout_user,
	login_required
)
from flask_restful import Api
from werkzeug.utils import redirect

from data import db_session, admin_api
from data.login import LoginForm
from data.register import RegisterForm
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex_lyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


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
	return db.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():
	"""Корневая страница"""
	db = db_session.create_session()
	return render_template('index.html')


# URL http://localhost:5000/register
@app.route('/register', methods=['GET', 'POST'])
def reqister():
	"""Страница регистрации"""
	regform = RegisterForm()
	if regform.validate_on_submit():
		if regform.password.data != regform.password_again.data:
			return render_template('register.html',
			                       title='Регистрация',
			                       form=regform,
			                       message='Пароли не совпадают')
		db = db_session.create_session()
		if db.query(User).filter(User.email == regform.email.data).first():
			return render_template('register.html',
			                       title='Регистрация',
			                       form=regform,
			                       message='Такой пользователь уже есть')
		user = User()
		user.name = regform.name.data
		user.email = regform.email.data
		user.status = 'Учащийся'
		user.about = regform.about.data
		user.set_password(regform.password.data)
		db.add(user)
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
	app.run(host='localhost')
