from decimal import Decimal

import pygsheets
from pygsheets import Worksheet, Spreadsheet
from sqlalchemy import create_engine, text
from sqlalchemy.engine import ResultProxy
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import TextClause

from models import Movie


def get_sheet(id: str) -> Spreadsheet:
    gc = pygsheets.authorize(outh_file='sheets_access.json')
    sh = gc.open_by_key(id)
    return sh


def get_ratings() -> list:
    res: ResultProxy = session.execute('SELECT id, title, ' \
                                       'max(if(name = \'Joppe\', score, NULL)) AS Joppe, ' \
                                       'max(if(name = \'Isak\', score, NULL))  AS Isak, ' \
                                       'max(if(name = \'Simon\', score, NULL)) AS Simon, ' \
                                       'max(if(name = \'Albin\', score, NULL)) AS Albin, ' \
                                       'max(if(name = \'Elon\', score, NULL))  AS Elon, ' \
                                       'imdb_score, ' \
                                       'year, ' \
                                       'director ' \
                                       'FROM (SELECT m.id AS id, m.title AS title, u.name AS name, r.user_score AS score, m.imdb_score '
                                       'AS imdb_score, ' \
                                       'm.year AS year, m.director AS director ' \
                                       'FROM ratings r ' \
                                       'JOIN movies m ON r.movie_id = m.id ' \
                                       'JOIN users u ON r.user_id = u.id) x ' \
                                       'GROUP BY id ' \
                                       'ORDER BY title')
    return res.fetchall()


def get_lastest_ratings() -> list:
    res: ResultProxy = session.execute(
        'SELECT name, title, r.user_score ' \
        'FROM movies m ' \
        'JOIN ratings r ON m.id=r.movie_id ' \
        'JOIN users u ON r.user_id=u.id ' \
        'ORDER BY r.added DESC, title LIMIT 10')
    return [list(row) for row in res]


def transform_row(data: tuple):
    _id = data[0]
    title = data[1]
    avg = str(
        session.execute(text("SELECT ROUND(AVG(user_score), 1) FROM ratings WHERE movie_id=:param"),
                        {"param": _id}).first()[0])
    row = [float(x) if isinstance(x, Decimal) else x for x in data]
    row = ['' if x is None else x for x in row]
    row = ['=HYPERLINK("http://www.imdb.com/title/{id}/", "{title}")'.format(id=_id, title=title)] \
          + row[2:7] \
          + [avg] \
          + row[7:]
    return row


if __name__ == '__main__':
    engine = create_engine('mysql+mysqldb://root:root@localhost:3306/imdb')
    session = Session(bind=engine, autoflush=False)
    conn = session.connection()
    sh = get_sheet(id='1KG4U0tmNyn0EDwckLz-rP4dqIuzSCzvv1WlL1VvYcmM')  # IMDB
    wk: Worksheet = sh.worksheet('index', 0)
    movies: list = session.query(Movie).order_by(Movie.title).all()
    ratings = list(map(transform_row, get_ratings()))

    wk.update_cells(f'A2:J{len(movies) + 1}', ratings)
    latest_ratings = get_lastest_ratings()
    wk.update_cells('L12:N21', latest_ratings)
