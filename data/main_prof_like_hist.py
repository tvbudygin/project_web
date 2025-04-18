from flask import render_template, request, redirect, abort
from project_web.connect_api.YandexGPT_api import gpt
from .user import User
from . import db_session
from flask_login import login_required, logout_user, current_user
from .food import Food
from .request_to_db import DataBase
import flask
from .app import login_manager

db = DataBase(User, Food, db_session)

blueprint = flask.Blueprint(
    'main_prof_like_hist',
    __name__,
    template_folder='templates')


# функция, которая поддерживает состояние аутентификации пользователя и администратора, путем обращения к сессии в бд
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# разлогинирование пользователя
@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# обработка главной страницы
@blueprint.route('/', methods=["GET", "POST"])
@blueprint.route('/main', methods=["GET", "POST"])
def main_menu():
    params = {"option1": "1 Вариант Рецепта",
              "option2": "2 Вариант Рецепта",
              "option3": "3 Вариант Рецепта",
              "text": "center", "pad": "100px"}

    if request.method == "POST":
        if "render" in request.form:
            product = request.form.get("input1")
            wish = request.form.get("input2")
            params = db.db_main_btn_render(current_user, product, wish, gpt)

        if "like" in request.form:
            try_params = db.db_main_btn_like(request, current_user)
            if try_params:
                params = try_params
    return render_template('index.html',
                           **params)


# обработка страницы профиля
@blueprint.route('/profile', methods=["GET", "POST"])
def profile():
    if not current_user.is_authenticated:
        return redirect("/login")
    params = db.db_profile(current_user)
    return render_template("profile.html",
                           **params)


# обработка кнопки удаления своего аккаунта
@blueprint.route("/delete", methods=["POST"])
def delete():
    db.db_delete_yourself(current_user)
    logout_user()
    return redirect("/")


# обработка удаление других пользователей(только для админа по кнопки в таблице),
# если меньше 10 запросов вылетит страница с ошибкой 418
@blueprint.route("/delete/<string:user_email>/<int:num_of_req>", methods=["POST"])
def delete_user(user_email, num_of_req):
    if num_of_req > 10:
        db.db_delete_user(user_email)
        return redirect("/history")
    else:
        abort(418, "У пользователя должно быть хотя бы 10 запросов")


# обработка страницы любимых рецептов
@blueprint.route("/likes", methods=["GET", "POST"])
def likes():
    if not current_user.is_authenticated:
        return redirect("/login")
    like = db.db_likes(current_user)
    return render_template("likes.html",
                           quant=len(like),
                           likes=like)


# обработка страницы историй запроса
@blueprint.route("/history", methods=["GET", "POST"])
def history():
    if not current_user.is_authenticated:
        return redirect("/login")
    params = db.db_history(current_user)
    return render_template("history.html",
                           **params)
