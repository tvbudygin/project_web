from flask import render_template, request, redirect
from project_web.connect_api.Captcha_api import check_captcha
import flask
from .user import User
from project_web.forms.registration import RegisterForm
from flask_login import login_user
from . import db_session
from project_web.forms.login import LoginForm

blueprint = flask.Blueprint(
    'reg_log',
    __name__,
    template_folder='../templates'
)


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if request.method == "POST":
        token = request.form.get("smart-token")
        user_ip = request.remote_addr

        if not token or not check_captcha(token, user_ip):
            return render_template('registration.html',
                                   form=form,
                                   message="Пройдите Капчу")

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registration.html',
                                   form=form,
                                   message="Такой пользователь уже есть")
        adm = False

        if request.form.get("admin"):
            adm = True

        user = User(
            name=form.name.data,
            email=form.email.data,
            admin=adm
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect('/')
    return render_template('registration.html',
                           form=form,
                           title='Регистрация')


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == "POST":
        token = request.form.get("smart-token")
        user_ip = request.remote_addr

        if not token or not check_captcha(token, user_ip):
            return render_template('login.html',
                                   form=form,
                                   message="Пройдите Капчу")

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")

        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)

    return render_template('login.html',
                           title='Авторизация',
                           form=form)
