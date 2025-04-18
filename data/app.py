from flask import Flask
from flask_login import LoginManager

# создание фласк приложения
app = Flask(__name__, static_folder='../static')
app.config['SECRET_KEY'] = 'timbudygin./././'
login_manager = LoginManager()
login_manager.init_app(app)
