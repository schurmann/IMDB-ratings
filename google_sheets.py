import simplejson as json

import pygsheets
import humanize
from pygsheets import Worksheet, Spreadsheet

from db.database import Database
from definitions import USERS

db = Database()
ALPHABETH = 'ABCDEFGHIJKMNOPQRSTUVWXYZ'
IMDB_LINK = 'http://www.imdb.com/title/{}'


def get_sheet(id: str) -> Spreadsheet:
    gc = pygsheets.authorize(outh_file='sheets_access.json')
    sh = gc.open_by_key(id)
    return sh


def to_link(link: str, title: str) -> str:
    return f'=HYPERLINK("{link}", "{title}")'


def transform_row(data: list):
    entry_id = data[0]
    title = data[1]
    avg = db.average_score(entry_id)
    row = ['' if x is None else x for x in data]
    row = [to_link(IMDB_LINK.format(entry_id), title)] \
          + row[2:7] \
          + [avg] \
          + row[7:]
    return row


def upload():
    sh = get_sheet(id='1KG4U0tmNyn0EDwckLz-rP4dqIuzSCzvv1WlL1VvYcmM')  # IMDB
    wk_movies: Worksheet = sh.worksheet('index', 0)
    wk_shows: Worksheet = sh.worksheet('index', 1)
    wk_top_movies: Worksheet = sh.worksheet('index', 4)
    upload_movies(wk_movies)
    upload_shows(wk_shows)
    upload_top_movies(wk_top_movies)


def upload_shows(wk_shows: Worksheet) -> None:
    if wk_shows.title == 'Serier':
        shows = list(map(transform_row, make_serializable(db.shows_matrix(USERS))))
        row_end, col_end = len(shows) + 1, ALPHABETH[len(USERS) + 4]
        wk_shows.update_cells(f'A2:{col_end}{row_end}', shows)
    else:
        print(f'Wrong title on worksheet: {wk_shows.title}')


def upload_movies(wk_movies: Worksheet) -> None:
    if wk_movies.title == 'Filmer':
        movies = list(map(transform_row, make_serializable(db.movies_matrix(USERS))))
        row_end, col_end = len(movies) + 1, ALPHABETH[len(USERS) + 4]
        wk_movies.update_cells(f'A2:{col_end}{row_end}', movies)
        latest_ratings = [(a, humanize.naturalday(b), c, d) for (a, b, c, d) in db.lastest_ratings()]
        wk_movies.update_cells('L12:O21', latest_ratings)
    else:
        print(f'Wrong title on worksheet: {wk_movies.title}')


def make_serializable(data: list) -> list:
    return json.loads(json.dumps([tuple(row) for row in data]))


def upload_top_movies(wk_top_movies: Worksheet):
    if wk_top_movies.title == 'Topplistor':
        top_movies = make_serializable(db.top_movies())
        top_movies = [(to_link(IMDB_LINK.format(row[0]), row[1]), row[2]) for row in top_movies]
        from ipdb import set_trace; set_trace()
        row_end, col_end = len(top_movies) + 2, ALPHABETH[len(top_movies[0]) - 1]
        wk_top_movies.update_cells(f'A3:{col_end}{row_end}', top_movies)
    else:
        print(f'Wrong title on worksheet: {wk_top_movies.title}')
