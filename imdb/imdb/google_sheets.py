import pygsheets
from pygsheets import Worksheet, Spreadsheet
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Movie, Rating, User

engine = create_engine('mysql+mysqldb://root:root@localhost:3306/imdb')
session = Session(bind=engine, autoflush=False)


def get_sheet(name: str) -> Spreadsheet:
    gc = pygsheets.authorize(outh_file='sheets_access.json')
    sh = gc.open(name)
    return sh


def get_ratings():
    res = session.execute('SELECT id, title, ' \
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
    range_ = []
    for r in res:
        row = list(map(lambda x: '' if x is None else x, r))
        range_.append(row[:7] + [''] + row[7:])
    return range_


sh = get_sheet('IMDB - Ratings')
wk: Worksheet = sh.worksheet_by_title('Sheet1')
movies: list = session.query(Movie).order_by(Movie.title).all()
range_ = get_ratings()

wk.update_cells(f'A2:K{len(movies) + 1}', range_)
