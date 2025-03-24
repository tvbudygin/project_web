from flask import Flask, render_template, request, redirect
from connect_api.Captcha_api import check_captcha
from connect_api.YandexGPT_api import gpt
from data.user import User
from data import db_session
from forms.login import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'timbudygin./././'


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
            return render_template('registration.html', title='Регистрация',
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
        return redirect('/login')
    return render_template('registration.html', form=form)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/', methods=["GET", "POST"])
@app.route('/main', methods=["GET", "POST"])
def main_menu():
    params = {"option1": "1 Вариант Рецепта", "option2": "2 Вариант Рецепта",
              "option3": "3 Вариант Рецепта", "text": "center", "pad": "100px"}
    if request.method == "POST":
        product = request.form.get("input1")
        wish = request.form.get("input2")
        print(gpt(product, wish))
    return render_template('index.html', **params)


if __name__ == '__main__':
    main()
