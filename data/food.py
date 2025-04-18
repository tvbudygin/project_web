import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


# создание таблицы food в бд
class Food(SqlAlchemyBase):
    __tablename__ = "food"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    history = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    result_his = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    like_title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    like = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
