from decimal import Decimal

import pygsheets
from pygsheets import Worksheet, Spreadsheet

from database import Database


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


if __name__ == '__main__':
    db = Database()
    sh = get_sheet(id='1KG4U0tmNyn0EDwckLz-rP4dqIuzSCzvv1WlL1VvYcmM')  # IMDB
    wk_movies: Worksheet = sh.worksheet('index', 0)
    wk_shows: Worksheet = sh.worksheet('index', 1)
    if wk_movies.title == 'Filmer':
        movies = list(map(transform_row, db.movies_matrix()))
        wk_movies.update_cells(f'A2:J{len(movies) + 1}', movies)
        latest_ratings = db.lastest_ratings()
        wk_movies.update_cells('L12:N21', latest_ratings)
    else:
        print(f'Wrong title on worksheet: {wk_movies.title}')

    if wk_shows.title == 'Serier':
        movies = list(map(transform_row, db.movies_matrix()))
        shows = list(map(transform_row, db.shows_matrix()))
        wk_shows.update_cells(f'A2:J{len(shows) + 1}', shows)
    else:
        print(f'Wrong title on worksheet: {wk_movies.title}')
