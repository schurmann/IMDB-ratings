from collections import OrderedDict

from sqlalchemy import create_engine, func
from sqlalchemy.engine import Engine, ResultProxy
from sqlalchemy.orm import sessionmaker, Session

from db.models import User, Base, Movie, Entry, Rating, Show
from definitions import DB_CONF


def user_stmt(users: OrderedDict) -> str:
    return ''.join([f"max(if(user_id = '{user_id}', score, NULL)) AS {name}, " for user_id, name in users.items()])


class Database:
    def __init__(self):
        self.__engine: Engine = create_engine(
            f"mysql+mysqldb://{DB_CONF['username']}:{DB_CONF['password']}@"
            f"{DB_CONF['host']}:{DB_CONF['port']}/{DB_CONF['database']}")
        self.__SessionMaker: sessionmaker = sessionmaker(bind=self.__engine)
        self.__session: Session = self.__SessionMaker(autocommit=False, autoflush=True)

    def create_tables(self, users: dict):
        Base.metadata.bind = self.__engine
        Base.metadata.drop_all()
        Base.metadata.create_all()
        users = [User(id=user_id, name=name) for user_id, name in users.items()]
        self.__session.add_all(users)
        self.__session.commit()

    def users(self) -> list:
        return self.__session.query(User).order_by(User.id).all()

    def movie(self, _id: str) -> Movie:
        return self.__session.query(Movie) \
            .filter(Movie.entry_id == _id) \
            .first()

    def rating(self, user_id: str, entry_id: str) -> Rating:
        return self.__session.query(Rating) \
            .join(User) \
            .join(Entry) \
            .filter(User.id == user_id) \
            .filter(Entry.id == entry_id) \
            .first()

    def add(self, base: Base):
        self.__session.add(base)

    def user(self, user_id: str):
        return self.__session.query(User) \
            .filter_by(id=user_id) \
            .first()

    def commit(self):
        self.__session.commit()

    def show(self, _id: str) -> Show:
        return self.__session.query(Show) \
            .filter(Show.entry_id == _id) \
            .first()

    def movies_matrix(self, users: OrderedDict) -> list:
        res: ResultProxy = self.__session.execute(
            f"SELECT id, title, {user_stmt(users)}" \
            "imdb_score, " \
            "year, " \
            "director " \
            "FROM (SELECT " \
            "e.id AS id, " \
            "e.title AS title, " \
            "u.id AS user_id, " \
            "r.user_score AS score, " \
            "e.imdb_score AS imdb_score, " \
            "m.year AS year, " \
            "m.director AS director " \
            "FROM ratings r " \
            "JOIN entries e ON r.entry_id = e.id " \
            "JOIN movies m ON e.id = m.entry_id " \
            "JOIN users u ON r.user_id = u.id) x " \
            "GROUP BY id, year, director ORDER BY title")
        return res.fetchall()

    def shows_matrix(self, users: OrderedDict) -> list:
        res: ResultProxy = self.__session.execute(
            f"SELECT id, title, {user_stmt(users)}" \
            "imdb_score, " \
            "start_year, " \
            "end_year " \
            "FROM (SELECT " \
            "e.id AS id, " \
            "e.title AS title, " \
            "u.id AS user_id, " \
            "r.user_score AS score, " \
            "e.imdb_score AS imdb_score, " \
            "s.start_year AS start_year, " \
            "s.end_year AS end_year " \
            "FROM ratings r " \
            "JOIN entries e ON r.entry_id = e.id " \
            "JOIN shows s ON e.id = s.entry_id " \
            "JOIN users u ON r.user_id = u.id) x " \
            "GROUP BY id, start_year, end_year ORDER BY title")
        return res.fetchall()

    def ratings(self, user_id: str, _filter: str = 'all') -> list:
        allowed = ['show', 'movie', 'all']
        _filter = _filter.lower()
        if _filter not in allowed:
            raise AssertionError(f'filter {_filter} not allowed: {allowed}')
        if _filter == 'all':
            return self.__session.query(Rating) \
                .join(User.ratings) \
                .filter(User.id == user_id) \
                .all()
        entity = Show if _filter == 'show' else Movie
        stmt = self.__session.query(entity.entry_id).subquery()
        return self.__session.query(Rating) \
            .join(User) \
            .join(stmt, Rating.entry_id == stmt.c.entry_id) \
            .filter(User.id == user_id) \
            .all()

    def latest_ratings(self) -> list:
        return self.__session.query(User.name, Rating.added, Entry.title, Rating.user_score, Entry.id) \
            .join(Rating.entry) \
            .join(User, User.id == Rating.user_id) \
            .group_by(User.name, Entry.title, Rating.added, Rating.user_score) \
            .order_by(Rating.added.desc(), Entry.title.asc()) \
            .limit(10) \
            .all()

    def top_movies(self) -> list:
        return self.__session.execute(
            "SELECT e.id, title, "
            "round(avg(user_score), 1) AS score "
            "FROM ratings r JOIN entries e ON r.entry_id=e.id "
            "GROUP BY e.id HAVING count(e.id)=(SELECT count(*) FROM users) ORDER BY score DESC;").fetchall()

    def average_score(self, entry_id: str):
        res = self.__session.query(func.avg(Rating.user_score)) \
            .filter_by(entry_id=entry_id) \
            .first()[0]
        return str(round(res, 1)) if res else None

    def close(self):
        self.__session.close()

    def session(self):
        return self.__session

