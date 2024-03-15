from flask import jsonify, make_response, Blueprint, current_app, render_template, request
from flask_login import login_required, current_user
from functools import wraps


def user_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        with current_app.test_request_context():
            return f(*args, **kwargs)

    return decorated_function


blueprint = Blueprint(
    'user_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/home')
@user_required
def home():
    return render_template('home_user.html')


@blueprint.route('/home/submit')
@user_required
def submit_quota():
    return render_template('submission_report.html')
