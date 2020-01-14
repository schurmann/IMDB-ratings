from collections import OrderedDict

from sqlalchemy import create_engine, func
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from db.models import User, Base, Movie, Entry, Rating, Show
from definitions import DB_CONF


def user_stmt(users: OrderedDict) -> str:
    return ''.join([f"max(if(user_id = '{user_id}', score, NULL)) AS {name}, " for user_id, name in users.items()])


class Database:
    def __init__(self):
        self.__engine: Engine = create_engine(
            f"sqlite:///../{DB_CONF['name']}.sqlite")
        self.__SessionMaker: sessionmaker = sessionmaker(bind=self.__engine)
        self.session: Session = self.__SessionMaker(autocommit=False, autoflush=True)

    def create_tables(self, users: dict):
        Base.metadata.bind = self.__engine
        Base.metadata.drop_all()
        Base.metadata.create_all()
        users = [User(id=user_id, name=name) for user_id, name in users.items()]
        self.session.add_all(users)
        self.session.commit()

    def users(self) -> list:
        return self.session.query(User).order_by(User.id).all()

    def movie(self, _id: str) -> Movie:
        return self.session.query(Movie) \
            .filter(Movie.entry_id == _id) \
            .first()

    def rating(self, user_id: str, entry_id: str) -> Rating:
        return self.session.query(Rating) \
            .join(User) \
            .join(Entry) \
            .filter(User.id == user_id) \
            .filter(Entry.id == entry_id) \
            .first()

    def add(self, base: Base):
        self.session.add(base)

    def user(self, user_id: str):
        return self.session.query(User) \
            .filter_by(id=user_id) \
            .first()

    def commit(self):
        self.session.commit()

    def show(self, _id: str) -> Show:
        return self.session.query(Show) \
            .filter(Show.entry_id == _id) \
            .first()

    def movies(self):
        return self.session.query(Movie).join(Entry).order_by(Entry.title.asc()).all()

    def shows(self):
        return self.session.query(Show).join(Entry).order_by(Entry.title.asc()).all()

    def latest_ratings(self, count: int) -> list:
        return self.session.query(User.name, Rating.added, Entry.title, Rating.user_score, Entry.id) \
            .join(Rating.entry) \
            .join(User, User.id == Rating.user_id) \
            .group_by(User.name, Entry.title, Rating.added, Rating.user_score) \
            .order_by(Rating.added.desc(), Entry.title.asc()) \
            .limit(count) \
            .all()

    def top_movies(self) -> list:
        return self.session.execute(
            "SELECT e.id, title, "
            "round(avg(user_score), 1) AS score "
            "FROM ratings r JOIN entries e ON r.entry_id=e.id "
            "GROUP BY e.id HAVING count(e.id)=(SELECT count(*) FROM users) ORDER BY score DESC;").fetchall()

    def average_score(self, entry_id: str):
        res = self.session.query(func.avg(Rating.user_score)) \
            .filter_by(entry_id=entry_id) \
            .first()[0]
        return str(round(res, 1)) if res else None

    def close(self):
        self.session.close()

    def session(self):
        return self.session
