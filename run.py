from flask import Flask, render_template, request, redirect
from connect_api.Captcha_api import check_captcha
from connect_api.YandexGPT_api import gpt
from sqlalchemy import or_
from data.user import User
from data import db_session
from forms.registration import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm
from data.food import Food

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
        db_sess = db_session.create_session()
        if "render" in request.form:
            product = request.form.get("input1")
            wish = request.form.get("input2")
            text = gpt(product, wish).split("\n")
            params = {"text": "left", "pad": "20px"}
            text1 = []
            res_his = []
            k = 1
            for i in text:
                if i != "":
                    text1.append(i)
                else:
                    if k <= 3:
                        params["option" + str(k)] = "<br>".join(text1)
                        res_his.append(text1[0][:-1])
                        k += 1
                    text1 = []
            params["option" + str(k)] = "<br>".join(text1)
            res_his.append(text1[0][:-1])
            food = Food(
                history=f"{product}; {wish}" if product != "" and wish != "" else f"{product}{wish}",
                user_id=current_user.id,
                result_his=", ".join(res_his)
            )
            db_sess.add(food)
            db_sess.commit()
        if "like" in request.form:
            like_text = request.form.get("like")
            if ("1 Вариант Рецепта" != like_text and "2 Вариант Рецепта" != like_text
                    and "3 Вариант Рецепта" != like_text):
                params = {"text": "left", "pad": "20px", "option1": request.form.get("option1"),
                          "option2": request.form.get("option2"), "option3": request.form.get("option3")}
                food = Food(
                    like_title=like_text[like_text.find(".") + 2:like_text.find("<br>") - 1],
                    like=like_text[like_text.find("<br>") + 4:],
                    user_id=current_user.id
                )
                db_sess.add(food)
                db_sess.commit()
    return render_template('index.html', **params)


@app.route('/profile', methods=["GET", "POST"])
def profile():
    db_sess = db_session.create_session()
    user = db_sess.query(User).first()
    params = {"name": user.name, "email": user.email, "create_data": user.created_date}
    return render_template("userprofil.html", **params)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    db_sess = db_session.create_session()
    food = db_sess.query(Food).filter(Food.user_id == User.id).all()
    user = db_sess.query(User).first()
    db_sess.delete(user)
    for i in food:
        db_sess.delete(i)
    db_sess.commit()
    logout_user()
    return redirect("/")


@app.route("/likes", methods=["GET", "POST"])
def likes():
    like = []
    db_sess = db_session.create_session()
    food = db_sess.query(Food).filter(Food.user_id == User.id,
                                      or_(Food.like_title.isnot(None), Food.like.isnot(None))).all()
    for i in food:
        like.append([i.like_title, i.like])
    return render_template("likes.html", quant=len(like), likes=like)


@app.route("/history", methods=["GET", "POST"])
def history():
    hist = []
    db_sess = db_session.create_session()
    food = db_sess.query(Food).filter(Food.user_id == User.id, Food.result_his.isnot(None)).all()
    for i in food:
        hist.append([i.history, i.result_his])
    return render_template("history.html", quant=len(hist), hist=hist)


if __name__ == '__main__':
    main()
