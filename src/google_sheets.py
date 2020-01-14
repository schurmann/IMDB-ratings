from os import path
from typing import List, Union

import humanize
import pygsheets
from pygsheets import Worksheet, Spreadsheet

from db.database import Database
from db.models import Movie, User, Rating
from definitions import ROOT_DIR

db = Database()
USERS: List[User] = sorted(db.users(), key=lambda user: user.name)
ALPHABETH: str = 'ABCDEFGHIJKMNOPQRSTUVWXYZ'
IMDB_LINK = 'http://www.imdb.com/title/{}'

Row = List[Union[str, int]]


def get_sheet(_id: str) -> Spreadsheet:
    gc = pygsheets.authorize(client_secret=path.join(ROOT_DIR, 'client_secret.json'))
    sh = gc.open_by_key(_id)
    return sh


def to_link(link: str, title: str) -> str:
    return f'=HYPERLINK("{link}", "{title}")'


def transform_row(data: list):
    entry_id = data[0]
    title = data[1]
    avg = db.average_score(entry_id)
    row = ['' if x is None else x for x in data]
    row = [to_link(IMDB_LINK.format(entry_id), title)] + row[2: len(USERS) + 2] + [avg] + row[len(USERS) + 2:]
    return row


def upload():
    sh = get_sheet(_id='1KG4U0tmNyn0EDwckLz-rP4dqIuzSCzvv1WlL1VvYcmM')
    wk_movies: Worksheet = sh.worksheet('index', 0)
    wk_top_movies: Worksheet = sh.worksheet('index', 2)
    upload_movies(wk_movies)
    upload_top_movies(wk_top_movies)


def get_row_rating(movie: Movie) -> Row:
    row: Row = list()
    imdb_link: str = IMDB_LINK.format(movie.entry.id)
    title_link: str = to_link(link=imdb_link, title=movie.entry.title)
    row.append(title_link)
    for user in USERS:
        rating: Rating = db.rating(user.id, movie.entry.id)
        user_score = rating.user_score if rating is not None else ''
        row.append(user_score)
    row.append(movie.entry.imdb_score)
    row.append(db.average_score(movie.entry.id))
    row.append(movie.year)
    row.append(movie.director)
    return row


def upload_movies(wk_movies: Worksheet) -> None:
    title = 'Filmer'
    if wk_movies.title == title:
        rows: List[Row] = []
        movies: List[Movie] = db.movies()
        for movie in movies:
            rows.append(get_row_rating(movie))

        row_end, col_end = len(movies) + 1, ALPHABETH[len(USERS) + 4]
        wk_movies.update_values(f'A2:{col_end}{row_end}', rows)
        latest_ratings = [
            [a, humanize.naturalday(b), to_link(IMDB_LINK.format(e), c), d] for (a, b, c, d, e) in db.latest_ratings(20)
        ]
        wk_movies.update_values('M12:P31', latest_ratings)
    else:
        print(f'Wrong title on worksheet. Got {wk_movies.title} ,expected {title}')


def upload_top_movies(wk_top_movies: Worksheet):
    title = 'Topplistor'
    if wk_top_movies.title == title:
        top_movies = db.top_movies()
        rows: List[Row] = list()
        for row in top_movies:
            imdb_link = IMDB_LINK.format(row[0])
            rows.append([to_link(imdb_link, row[1]), row[2]])

        row_end, col_end = len(top_movies) + 2, ALPHABETH[len(top_movies[0]) - 1]
        wk_top_movies.update_values(f'A3:{col_end}{row_end}', rows)
    else:
        print(f'Wrong title on worksheet. Got {wk_top_movies.title} ,expected {title}')
