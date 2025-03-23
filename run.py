from flask import Flask, render_template, request
from connect_api.Captcha_api import check_captcha
from connect_api.YandexGPT_api import gpt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'timbudygin./././'


@app.route("/")
@app.route("/reg", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        token = request.form.get("smart-token")
        user_ip = request.remote_addr
        if not token or not check_captcha(token, user_ip):
            return render_template("registration.html")
    return render_template("registration.html")


@app.route('/log')
def login():
    return render_template('login.html')


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
    app.run(port=8080, host='127.0.0.1')
