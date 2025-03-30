from flask import Flask, render_template, request, redirect
from connect_api.Captcha_api import check_captcha
from connect_api.YandexGPT_api import gpt
from data.user import User
from data import db_session
from forms.registration import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'timbudygin./././'


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
        product = request.form.get("input1")
        wish = request.form.get("input2")
        text = gpt(product, wish).split("\n")
        params = {"text": "left", "pad": "20px"}
        print(text)
        text1 = []
        k = 1
        for i in text:
            if i != "":
                text1.append(i)
            else:
                print("\n".join(text1))
                if k <= 3:
                    params["option" + str(k)] = "<br>".join(text1)
                    k += 1
                text1 = []
        params["option" + str(k)] = "<br>".join(text1)

    return render_template('index.html', **params)


if __name__ == '__main__':
    main()
