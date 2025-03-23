from project_web.run import app
from data import db_session

if __name__ == "__main__":
    db_session.global_init("db/reg.db")
    app.run(port=8080, host='127.0.0.1')
