from flask import Flask, render_template, request, redirect, abort
from connect_api.Captcha_api import check_captcha
from connect_api.YandexGPT_api import gpt
from data.user import User
from data import db_session
from forms.registration import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm
from data.food import Food
from data.request_to_db import DataBase

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'timbudygin./././'
db = DataBase(User, Food, db_session)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/reg.db")
    app.run(port=8080, host='127.0.0.1', debug=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == "POST":
        token = request.form.get("smart-token")
        user_ip = request.remote_addr
        if not token or not check_captcha(token, user_ip):
            return render_template('registration.html', form=form, message="Пройдите Капчу")
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
    return render_template('registration.html', form=form, title='Регистрация')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST":
        token = request.form.get("smart-token")
        user_ip = request.remote_addr
        if not token or not check_captcha(token, user_ip):
            return render_template('login.html', form=form, message="Пройдите Капчу")
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/', methods=["GET", "POST"])
@app.route('/main', methods=["GET", "POST"])
def main_menu():
    params = {"option1": "1 Вариант Рецепта", "option2": "2 Вариант Рецепта",
              "option3": "3 Вариант Рецепта", "text": "center", "pad": "100px"}
    if request.method == "POST":
        if "render" in request.form:
            product = request.form.get("input1")
            wish = request.form.get("input2")
            params = db.db_main_btn_render(current_user, product, wish, gpt)
        if "like" in request.form:
            try_params = db.db_main_btn_like(request, current_user)
            if try_params:
                params = try_params
    return render_template('index.html', **params)


@app.route('/profile', methods=["GET", "POST"])
def profile():
    if not current_user.is_authenticated:
        return redirect("/login")
    params = db.db_profile(current_user)
    return render_template("profile.html", **params)


@app.route("/delete", methods=["POST"])
def delete():
    db.db_delete_yourself(current_user)
    logout_user()
    return redirect("/")


@app.route("/delete/<string:user_email>/<int:num_of_req>", methods=["POST"])
def delete_user(user_email, num_of_req):
    if num_of_req > 10:
        db.db_delete_user(user_email)
        return redirect("/history")
    else:
        abort(418, "У пользователя должно быть хотя бы 10 запросов")


@app.route("/likes", methods=["GET", "POST"])
def likes():
    if not current_user.is_authenticated:
        return redirect("/login")
    like = db.db_likes(current_user)
    return render_template("likes.html", quant=len(like), likes=like)


@app.route("/history", methods=["GET", "POST"])
def history():
    if not current_user.is_authenticated:
        return redirect("/login")
    params = db.db_history(current_user)
    return render_template("history.html", **params)


if __name__ == '__main__':
    main()
