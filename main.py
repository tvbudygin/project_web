from data import db_session
from data import reg_log, main_prof_like_hist
from data.app import app

if __name__ == "__main__":
    app.register_blueprint(reg_log.blueprint)
    app.register_blueprint(main_prof_like_hist.blueprint)
    db_session.global_init("db/reg.db")
    app.run(port=8080, host='127.0.0.1')
