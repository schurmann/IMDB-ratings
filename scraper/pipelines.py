# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime

from scrapy import Spider

from db.database import Database
from db.models import Movie, Rating, Entry, User, Show


def create_entry(item: dict):
    return Entry(id=item['imdb_id'],
                 imdb_score=item['imdb_score'],
                 title=item['title'],
                 added=datetime.now(),
                 votes=item['votes'])


def create_show(entry: Entry, item: dict):
    return Show(start_year=item['start_year'],
                end_year=item['end_year'],
                entry=entry)


def create_movie(entry: Entry, item: dict):
    return Movie(director=item['director'],
                 year=item['year'],
                 entry=entry)


def create_rating(item: dict, entry: Entry, user: User):
    return Rating(user_score=item['user_score'],
                  added=item['rated_date'],
                  updated=datetime.now(),
                  entry=entry,
                  user=user)


class ImdbPipeline:
    def __init__(self):
        self.db = Database()

    def close_spider(self, spider: Spider):
        self.db.commit()
        self.db.close()

    def process_item(self, item: dict, spider: Spider):
        user = item['user_id']
        rating = self.process_movie(item, user) if item['is_movie'] else self.process_show(item, user)

        if rating.user_score != item['user_score']:
            rating.user_score = item['user_score']
            rating.updated = datetime.now()
        if rating.entry.votes != item['votes']:
            rating.entry.votes = item['votes']
        self.db.add(rating)
        return item

    def process_movie(self, item: dict, user: User) -> Rating:
        movie = self.db.movie(item['imdb_id'])
        if movie is None:
            entry = create_entry(item)
            movie = create_movie(entry, item)
        rating = self.db.rating(item['user_id'].id, item['imdb_id'])
        if rating is None:
            rating = create_rating(item, movie.entry, user)
        return rating

    def process_show(self, item: dict, user: User) -> Rating:
        show = self.db.show(item['imdb_id'])
        if show is None:
            entry = create_entry(item)
            show = create_show(entry, item)
        rating = self.db.rating(item['user_id'], item['imdb_id'])
        if rating is None:
            rating = create_rating(item, show.entry, user)
        return rating
