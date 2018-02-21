from decimal import Decimal

import pygsheets
import humanize
from pygsheets import Worksheet, Spreadsheet

from db.database import Database
from definitions import USERS

db = Database()
ALPHABETH = 'ABCDEFGHIJKMNOPQRSTUVWXYZ'


def get_sheet(id: str) -> Spreadsheet:
    gc = pygsheets.authorize(outh_file='sheets_access.json')
    sh = gc.open_by_key(id)
    return sh


def transform_row(data: tuple):
    entry_id = data[0]
    title = data[1]
    avg = db.average_score(entry_id)
    row = [float(x) if isinstance(x, Decimal) else x for x in data]
    row = ['' if x is None else x for x in row]
    row = ['=HYPERLINK("http://www.imdb.com/title/{id}/", "{title}")'.format(id=entry_id, title=title)] \
          + row[2:7] \
          + [avg] \
          + row[7:]
    return row


def upload():
    sh = get_sheet(id='1KG4U0tmNyn0EDwckLz-rP4dqIuzSCzvv1WlL1VvYcmM')  # IMDB
    wk_movies: Worksheet = sh.worksheet('index', 0)
    wk_shows: Worksheet = sh.worksheet('index', 1)
    if wk_movies.title == 'Filmer':
        movies = list(map(transform_row, db.movies_matrix(USERS)))
        row_end, col_end = len(movies) + 1, ALPHABETH[len(USERS) + 4]
        wk_movies.update_cells(f'A2:{col_end}{row_end}', movies)
        latest_ratings = [(a, humanize.naturalday(b), c, d) for (a, b, c, d) in db.lastest_ratings()]
        wk_movies.update_cells('L12:O21', latest_ratings)
    else:
        print(f'Wrong title on worksheet: {wk_movies.title}')

    if wk_shows.title == 'Serier':
        shows = list(map(transform_row, db.shows_matrix(USERS)))
        row_end, col_end = len(shows) + 1, ALPHABETH[len(USERS) + 4]
        wk_shows.update_cells(f'A2:{col_end}{row_end}', shows)
    else:
        print(f'Wrong title on worksheet: {wk_movies.title}')
